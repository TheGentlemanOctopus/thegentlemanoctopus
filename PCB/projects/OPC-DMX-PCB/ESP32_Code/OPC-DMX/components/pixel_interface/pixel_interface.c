/*
 * pixel_interface.c
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben Holden
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

/* Definitions of pixels */
const pixel_type_t pixel_type_lookup[PIXEL_NAME_MAX] = {
	[PIXEL_WS2812_V1] = {
			.pixel_bit[PIXEL_BIT_lOW] = { .level0 = 1, .duration0 = 350/RMT_CLK_DIVIDER, .level1 = 0, .duration1 = 800/RMT_CLK_DIVIDER},
			.pixel_bit[PIXEL_BIT_HIGH] = { .level0 = 1, .duration0 = 700/RMT_CLK_DIVIDER, .level1 = 0, .duration1 = 600/RMT_CLK_DIVIDER},
			.reset = 50000/RMT_CLK_DIVIDER,
			.colour_num = 3
	}
};

void pixel_init_channel(pixel_channel_config_t* channel)
{
	/* Initialise the RMT channel pixels will be sent down */
	pixel_init_rmt_channel(channel);
	/* Create a data buffer for the pixel RGB data */
	pixel_create_data_buffer(channel);

	/* Set channel counters to 0 */
	channel->counters.bit_counter = 0;
	channel->counters.pixel_counter = 0;
	channel->counters.rmt_counter = 0;

	/* Set the rmt block to max to the RMT block size so it fills the whole buffer on the first run */
	channel->counters.rmt_block_max = RMT_MEM_BLOCK_SIZE;
}

void pixel_init_rmt_channel(pixel_channel_config_t* channel)
{

	rmt_config_t rmt_parameters;

	/* Load with the desired settings for pixel sending */
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
	/* Stop the channel from streaming out data prematurely */
	rmt_tx_stop(channel->rmt_channel);
	/* This also needs to be set to false... */
	rmt_set_tx_loop_mode(channel->rmt_channel, false);

	/* Allocate buffer for the RMT data */
	channel->rmt_mem_block = (rmt_item32_t*) &RMTMEM.chan[channel->rmt_channel];
	/* Set block to zeroes */
	memset(channel->rmt_mem_block, 0 , sizeof(rmt_item32_t)*RMT_MEM_BLOCK_SIZE);

}

void pixel_create_data_buffer(pixel_channel_config_t* channel)
{
	/* Allocate memory size of the channel length  */
	channel->pixel_data = (pixel_data_t*) malloc(channel->channel_length * sizeof(pixel_data_t));
	/* Clear buffer */
	memset(channel->pixel_data, 0 , channel->channel_length * sizeof(pixel_data_t));
}

void pixel_delete_data_buffer(pixel_channel_config_t* channel)
{
	/* Deallocate memory buffer memory  */
	free(channel->pixel_data);
	channel->pixel_data = NULL;
}

void pixel_send_data(pixel_channel_config_t* channel)
{
	/* This function will be used to write pixel data into the RMT buffer */

	/* Bit to index the RGB to RMT data */
	uint8_t pixel_bit;
	/* Mask for the pixel data */
	uint32_t pixel_bit_mask = PIXEL_BIT_MASK_INIT;
	/* Temporary store for the pixel to be sent */
	uint32_t temp_pixel_data = 0;

	/* For loop pixels in the channel length */
	for(; channel->counters.pixel_counter < channel->channel_length;
			channel->counters.pixel_counter++)
	{
		/* Copy the pixel data to the temp store */
		temp_pixel_data = channel->pixel_data[channel->counters.pixel_counter].data;

		/* For loop for RMT buffer loading, exits either when at the end of the pixel data (will do RGB or RGBW depending on the pixel type), or the RMT buffer is full */
		for(	; (channel->counters.bit_counter < CHAR_BIT * channel->pixel_type.colour_num) && (channel->counters.rmt_counter < channel->counters.rmt_block_max);
				channel->counters.bit_counter++, channel->counters.rmt_counter++)
		{
			/* Bitwise logic for checking if the current bit is a 1 or a 0 */
			if (temp_pixel_data & pixel_bit_mask)
			{
				pixel_bit = 1;
			} else {
				pixel_bit = 0;
			}

			/* Debug stuff */

			printf("pixel_bit = %d temp_pixel = %08x\n", pixel_bit, temp_pixel_data);
			printf("Pixel counter = %d Bit counter = %d RMT counter = %d\n",channel->counters.pixel_counter,channel->counters.bit_counter,channel->counters.rmt_counter);

			/* load RMT memory block with the bit data */
			channel->rmt_mem_block[channel->counters.rmt_counter] = channel->pixel_type.pixel_bit[pixel_bit];
			/* Shift temp data along for next bit next iteration*/
			temp_pixel_data <<= 1;
		}

		/* If the bit counter caused the loop to break, then zero the bit counter */
		if (channel->counters.bit_counter >= CHAR_BIT * channel->pixel_type.colour_num)
		{
			channel->counters.bit_counter = 0;
		}

		/* If the RMT counter caused the loop to break, then update the RMT_block max for next time */
		if (channel->counters.rmt_counter >= channel->counters.rmt_block_max)
		{
			/* Check what setting the RMT block max is in */
			if (channel->counters.rmt_block_max == RMT_MEM_BLOCK_SIZE)
			{
				channel->counters.rmt_block_max = RMT_MEM_BLOCK_SIZE/2;
				channel->counters.rmt_counter = 0;
			} else {
				channel->counters.rmt_block_max = RMT_MEM_BLOCK_SIZE;
			}
			printf("Pixel counter = %d Bit counter = %d RMT counter = %d\n",channel->counters.pixel_counter,channel->counters.bit_counter,channel->counters.rmt_counter);

			/* Break out of the loop  to avoid overflowing the buffer */
			break;
		}

	}

	/* If at the end of the pixel channel then send the reset pulse */
	if (channel->counters.pixel_counter >= channel->channel_length)
	{
		/* Catch for underflow if pixel channel ends on a 0*/
		if (channel->counters.rmt_counter == 0)
		{
			/* Stretch out the last bit in the pixel rmt buffer */
			channel->rmt_mem_block[RMT_MEM_BLOCK_SIZE-1].duration1 = channel->pixel_type.reset;
		} else {
			/* Stretch out the last bit in the pixel rmt buffer */
			channel->rmt_mem_block[channel->counters.rmt_counter-1].duration1 = channel->pixel_type.reset;
		}
	}
}
