/*
 * pixel_interface.c
 *
 * @brief Pixel Interface Using the ESP32's RMT module.
 *
 *
 *  	Created on: 20 Sep 2017
 *  	Author: Ben Holden
 *  The Gentleman Octopus Ltd
 *
 */

#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "pixel_interface.h"
#include "driver/rmt.h"
#include "soc/rmt_struct.h"
#include <limits.h>
#include <stdio.h>
#include <string.h>

#define LOG_LOCAL_LEVEL ESP_LOG_DEBUG
#include "esp_log.h"

/* Tag for log messages */
static const char* PIXEL_TAG = "pixel";
SemaphoreHandle_t xPixelSemaphore[PIXEL_CHANNEL_MAX];

/* Store of handles for the RMT interrupt handler. Should be indexed by the pixel channels RMT_channel number*/
pixel_channel_config_t* pixel_rmt_handles[RMT_CHANNEL_MAX];

/**
 * Definitions of the type of pixels from various datasheets.
 * Indexed by the pixel_name_t enum in pixel_interface.h
 */
const pixel_type_t pixel_type_lookup[PIXEL_NAME_MAX] = {
	[PIXEL_WS2812_V1] = {
			.pixel_bit[PIXEL_BIT_lOW] = { .level0 = 1, .duration0 = 350/RMT_CLK_DIVIDER, .level1 = 0, .duration1 = 800/RMT_CLK_DIVIDER},
			.pixel_bit[PIXEL_BIT_HIGH] = { .level0 = 1, .duration0 = 700/RMT_CLK_DIVIDER, .level1 = 0, .duration1 = 600/RMT_CLK_DIVIDER},
			.reset = 50000/RMT_CLK_DIVIDER,
			.colour_num = 3
	}
};

/**
 * Definitions of the GPIO pins for each pixel channel
 * Should be changed depending on users needs.
 */
const gpio_num_t pixel_gpio[PIXEL_CHANNEL_MAX] = {
		[PIXEL_CHANNEL_0] = GPIO_NUM_2,
		[PIXEL_CHANNEL_1] = GPIO_NUM_5,
		[PIXEL_CHANNEL_2] = GPIO_NUM_4,
		[PIXEL_CHANNEL_3] = GPIO_NUM_19,
		[PIXEL_CHANNEL_4] = GPIO_NUM_18,
		[PIXEL_CHANNEL_5] = GPIO_NUM_22,
		[PIXEL_CHANNEL_6] = GPIO_NUM_21,
		[PIXEL_CHANNEL_7] = GPIO_NUM_23
};


pixel_channel_config_t* pixel_generate_channel_conf(pixel_channel_t pixel_channel, uint32_t channel_length, pixel_name_t pixel_type)
{
	pixel_channel_config_t* channel;
	/* Allocate memory for the structure */
	channel = malloc(sizeof(pixel_channel_config_t));

	channel->pixel_channel = pixel_channel;
	channel->gpio_output_pin = pixel_gpio[pixel_channel];
	/* To avoid confusion RMT channel is the same number as the pixel channel*/
	channel->rmt_channel = (rmt_channel_t)pixel_channel;
	channel->channel_length = channel_length;

	channel->pixel_type = pixel_type_lookup[pixel_type];

	return channel;
}


void pixel_init_channel(pixel_channel_config_t* channel)
{
	/* Initialise the RMT channel pixels will be sent down */
	pixel_init_rmt_channel(channel);
	/* Create a data buffer for the pixel RGB data */
	pixel_create_data_buffer(channel);

	/* Tie channel threshold interrupt to the TX threshold handler function */
	esp_intr_alloc_intrstatus(ETS_RMT_INTR_SOURCE, ESP_INTR_FLAG_SHARED, (uint32_t)&RMT.int_st.val, BIT((channel->rmt_channel + 24)), pixel_intr_handler_half, channel, NULL);
	esp_intr_alloc_intrstatus(ETS_RMT_INTR_SOURCE, ESP_INTR_FLAG_SHARED, (uint32_t)&RMT.int_st.val, BIT((channel->rmt_channel * 3)), pixel_intr_handler_end, channel, NULL);

	/* Create semaphore for updating the pixel channels */
	xPixelSemaphore[channel->pixel_channel] = xSemaphoreCreateBinary();

	ESP_LOGD(PIXEL_TAG, "RMT starting at address %p \n", channel->rmt_mem_block);
}

void pixel_init_rmt_channel(pixel_channel_config_t* channel)
{

	rmt_config_t rmt_parameters;

	/* Load with the desired settings for pixel RMT sending */
	rmt_parameters.channel = channel->rmt_channel;
	rmt_parameters.clk_div = RMT_DIVIDER;
	rmt_parameters.gpio_num = channel->gpio_output_pin;
	rmt_parameters.mem_block_num = RMT_MEM_BLOCK_NUM;
	rmt_parameters.rmt_mode = RMT_MODE_TX;
	rmt_parameters.tx_config.carrier_en = false;
	rmt_parameters.tx_config.loop_en = true;
	rmt_parameters.tx_config.idle_output_en = true;
	rmt_parameters.tx_config.idle_level = RMT_IDLE_LEVEL_LOW;

	/* Initialise the RMT with settings above */
	rmt_config(&rmt_parameters);
	/* Reset the memory index */
	rmt_memory_rw_rst(channel->rmt_channel);
	/* Stop the channel from streaming out data prematurely */
	rmt_tx_stop(channel->rmt_channel);
	/* Enable wrap around mode for continuous sending */
	//RMT.apb_conf.mem_tx_wrap_en = true;
	/* This also needs to be set to false... */
	rmt_set_tx_loop_mode(channel->rmt_channel, false);
	/* Allocate buffer for the RMT data */
	channel->rmt_mem_block = (rmt_item32_t*) &RMTMEM.chan[channel->rmt_channel].data32;
	/* Set block to zeroes */
	memset(channel->rmt_mem_block, 0 , sizeof(rmt_item32_t)*RMT_MEM_BLOCK_SIZE);

}

void pixel_create_data_buffer(pixel_channel_config_t* channel)
{
	/* Allocate memory size of the channel length  */
	channel->pixel_data = (pixel_data_t*) malloc(channel->channel_length * sizeof(pixel_data_t));
	if (channel->pixel_data == NULL)
	{
		ESP_LOGD(PIXEL_TAG, "Malloc Error");
	}
	/* Clear buffer */
	memset(channel->pixel_data, 0 , channel->channel_length * sizeof(pixel_data_t));
}

void pixel_delete_data_buffer(pixel_channel_config_t* channel)
{
	/* Deallocate memory buffer memory  */
	free(channel->pixel_data);
	channel->pixel_data = NULL;
}

void pixel_start_channel(pixel_channel_config_t* channel)
{
	/* Debug pin outputs*/

	gpio_pad_select_gpio(GPIO_NUM_27);
	/* Set the GPIO as a push/pull output */
	gpio_set_direction(GPIO_NUM_27, GPIO_MODE_OUTPUT);
	gpio_set_level(GPIO_NUM_27, 0);

	gpio_pad_select_gpio(GPIO_NUM_13);
	/* Set the GPIO as a push/pull output */
	gpio_set_direction(GPIO_NUM_13, GPIO_MODE_OUTPUT);
	gpio_set_level(GPIO_NUM_13, 0);

	ESP_LOGD(PIXEL_TAG,"in pixel channel %d\n", channel->pixel_channel);

	/* EVERYTHING BELOW THIS LINE GOES IN FOR LOOP */
	/* Set channel counters to 0 */
	channel->counters.bit_counter = 0;
	channel->counters.pixel_counter = 0;
	channel->counters.rmt_counter = 0;

	/* Set the rmt block to max to the RMT block size so it fills the whole buffer on the first run */
	channel->counters.rmt_block_max = PIXEL_MEM_BLOCK_SIZE;

	/* Load first RMT block with converted data so it's got something to send */
	pixel_convert_data(channel);

	/* Reset the memory index */
	rmt_memory_rw_rst(channel->rmt_channel);
	/* Ensure interrupts are cleared*/
	RMT.int_clr.val |= BIT((channel->rmt_channel * 3));
	RMT.int_clr.val |= BIT((channel->rmt_channel + 24));

	/* Set an interrupt to fire every half block */
	rmt_set_tx_thr_intr_en(channel->rmt_channel, true, (PIXEL_MEM_BLOCK_SIZE/2));
	ESP_LOGD(PIXEL_TAG,"RMT limit set to %d\n", RMT.tx_lim_ch[channel->rmt_channel].limit);
	/* Keep wraparound mode disabled */
	RMT.apb_conf.mem_tx_wrap_en = false;

	/* Start continuously sending out the RMT data */
	rmt_tx_start(channel->rmt_channel, true);
	rmt_set_tx_loop_mode(channel->rmt_channel, true);
	for(;;)
	{
		/*Wait for semaphore to update the pixel data */


	}
}

IRAM_ATTR void pixel_intr_handler_end(pixel_channel_config_t* channel)
{
	static uint8_t tx_thr_stat = 0;
	/* toggle a pin for debug */
	tx_thr_stat ^= 0x01;
	gpio_set_level(GPIO_NUM_13, tx_thr_stat);

	/* Clear Interrupt Flag */
	RMT.int_clr.val |= BIT((channel->rmt_channel * 3));
	/* toggle a pin for debug */
	tx_thr_stat ^= 0x01;
	gpio_set_level(GPIO_NUM_13, tx_thr_stat);
}

IRAM_ATTR void pixel_intr_handler_half(pixel_channel_config_t* channel)
{
	portMUX_TYPE myMutex = portMUX_INITIALIZER_UNLOCKED;
	static uint8_t tx_thr_stat = 0;
	/* toggle a pin for debug */
	tx_thr_stat ^= 0x01;
	gpio_set_level(GPIO_NUM_27, tx_thr_stat);

	/* Clear Halfway Interrupt Flag */
	RMT.int_clr.val |= BIT((channel->rmt_channel + 24));

	taskENTER_CRITICAL(&myMutex);

	/* Send the next half of the data */
	pixel_convert_data(channel);

	taskEXIT_CRITICAL(&myMutex);

	/* toggle a pin for debug */
	tx_thr_stat ^= 0x01;
	gpio_set_level(GPIO_NUM_27, tx_thr_stat);
}

IRAM_ATTR void pixel_update_data(pixel_channel_config_t* channel)
{

}

IRAM_ATTR void pixel_convert_data(pixel_channel_config_t* channel)
{
	/* This function will be used to write pixel data into the RMT buffer */
	/* Bit to index the RGB to RMT data */
	uint8_t pixel_bit;

	/* Unlimited loop for pixels in the channel length until either RMT buffer full
	 * or at the end of a pixel strip
	 */
	while(true)
	{
		/* Copy the pixel data to the temp store, bit shift in case RMT counter broke loop*/
		channel->counters.temp_pixel_data = channel->pixel_data[channel->counters.pixel_counter].data << channel->counters.bit_counter;

		/* For loop for RMT buffer loading, exits either when at the end of the pixel data (will do RGB or RGBW depending on the pixel type), or the RMT buffer is full */
		for(	; (channel->counters.bit_counter < CHAR_BIT * channel->pixel_type.colour_num) && (channel->counters.rmt_counter < channel->counters.rmt_block_max);
				channel->counters.bit_counter++, channel->counters.rmt_counter++)
		{
			/* Bitwise logic for checking if the current bit is a 1 or a 0 */
			pixel_bit = ((channel->counters.temp_pixel_data >> 31) & PIXEL_BIT_MASK);

			/* Debug stuff */

	//		ESP_LOGV(PIXEL_TAG,"pixel_bit = %d temp_pixel = %08x\n", pixel_bit, channel->counters.temp_pixel_data);
	//		ESP_LOGV(PIXEL_TAG,"Pixel counter = %d Bit counter = %d RMT counter = %d RMT max = %d\n",channel->counters.pixel_counter,channel->counters.bit_counter,channel->counters.rmt_counter, channel->counters.rmt_block_max);

			/* load RMT memory block with the bit data */
			channel->rmt_mem_block[channel->counters.rmt_counter] = channel->pixel_type.pixel_bit[pixel_bit];

	//		ESP_LOGV(PIXEL_TAG,"RMT_Data = %08x\n", channel->rmt_mem_block[channel->counters.rmt_counter].val);

			/* Shift temp data along for next bit next iteration*/
			channel->counters.temp_pixel_data <<= 1;
		}

		/* If the bit counter caused the loop to break, then zero the bit counter*/
		if (channel->counters.bit_counter >= (CHAR_BIT * channel->pixel_type.colour_num))
		{
			channel->counters.bit_counter = 0;

			/* If at the end of the pixel channel then send the reset pulse */
			if (channel->counters.pixel_counter >= channel->channel_length-1)
			{
	//			ESP_LOGV(PIXEL_TAG,"Reset Pulse");
	//			ESP_LOGV(PIXEL_TAG,"Pixel counter = %d Bit counter = %d RMT counter = %d RMT max = %d\n",channel->counters.pixel_counter,channel->counters.bit_counter,channel->counters.rmt_counter, channel->counters.rmt_block_max);

				/* Stretch out the last bit in the pixel rmt buffer */
				channel->rmt_mem_block[channel->counters.rmt_counter-1].duration1 = channel->pixel_type.reset;

				/* Zero pixel counters to start sending pixels all over again*/
				channel->counters.pixel_counter = 0;

				/* Set up the loop to stop when all data is sent from the next block*/
				rmt_set_tx_loop_mode(channel->rmt_channel, false);
				/* Stop the half channel interrupt so we don't fill anymore data*/
				rmt_clr_intr_enable_mask(BIT(channel->rmt_channel + 24));


				if (channel->counters.rmt_counter < channel->counters.rmt_block_max)
				{
					/* If we're not at the last RMT block then set the next data block to be 0 so that the RMT will stop
					 * If we are at the last one it will stop anyway because no more data and loop mode is off.
					 */
					channel->rmt_mem_block[channel->counters.rmt_counter].val = 0;
				}
				break;

			} else {
				/* Go to the next pixel, for next iteration of loop */
				channel->counters.pixel_counter++;
			}

		}

		/* If the RMT counter caused the loop to break, then update the RMT_block max for next time */
		if (channel->counters.rmt_counter >= channel->counters.rmt_block_max)
		{
			/* Check what setting the RMT block max is in */
			if (channel->counters.rmt_block_max == PIXEL_MEM_BLOCK_SIZE)
			{
				/* Reset to 0 and set the next iteration to go to half of a block */
				channel->counters.rmt_block_max = PIXEL_MEM_BLOCK_SIZE/2;
				channel->counters.rmt_counter = 0;
			} else {
				/* Next iteration will complete the block */
				channel->counters.rmt_block_max = PIXEL_MEM_BLOCK_SIZE;
			}
			/* Break out of the loop to avoid overflowing the buffer */
			break;
		}
	}
}

