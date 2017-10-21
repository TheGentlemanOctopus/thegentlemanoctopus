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


/* Do something here... Flashy LEDs probably :^) */

void init_pixel_rmt_channel(pixel_channel_config_t* channel)
{
	rmt_config_t rmt_parameters;

	rmt_parameters.channel = channel->rmt_channel;
	rmt_parameters.clk_div = RMT_DIVIDER;
	rmt_parameters.gpio_num = channel->gpio_output_pin;
	rmt_parameters.mem_block_num = RMT_MEM_BLOCK_NUM;
	rmt_parameters.rmt_mode = RMT_MODE_TX;
	rmt_parameters.tx_config.carrier_en = false;
	rmt_parameters.tx_config.loop_en = true;
	rmt_parameters.tx_config.idle_output_en = true;
	rmt_parameters.tx_config.idle_level = RMT_IDLE_LEVEL_LOW;
	/* initialise the RMT with settings above */
	rmt_config(&rmt_parameters);

}



void send_pixel_data(pixel_channel_config_t* channel)
{
	/* This function will be used to write pixel data into the RMT buffer */
}
