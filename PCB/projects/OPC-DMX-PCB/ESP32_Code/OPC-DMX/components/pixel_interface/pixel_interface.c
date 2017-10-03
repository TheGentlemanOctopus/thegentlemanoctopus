/*
 * pixel_interface.c
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben
 */

#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "pixel_interface.h"



/* Do something here... Flashy LEDs probably :^) */

void init_pixel_channels(void)
{
	pixel_channel_config_t channels[PIXEL_CHANNEL_MAX];

	for (int i=0; i<PIXEL_CHANNEL_MAX; i++)
	{
		channels[i].pixel_channel = i;

	}


}

