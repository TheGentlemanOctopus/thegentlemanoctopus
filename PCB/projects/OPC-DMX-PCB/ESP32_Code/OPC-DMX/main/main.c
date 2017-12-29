#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/rmt.h"
#include "esp_eth.h"
#include "esp_log.h"
#include "pixel_interface.h"

#include "xtensa/core-macros.h"

esp_err_t event_handler(void *ctx, system_event_t *event)
{
    return ESP_OK;
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
pixel_data_t Wheel(uint8_t WheelPos) {

	pixel_data_t out;
	WheelPos = 255 - WheelPos;
	if(WheelPos < 85) {
		out.r = 255 - WheelPos * 3;
		out.g =  0;
		out.b = WheelPos * 3;
		return out;
	} else if(WheelPos < 170) {
		WheelPos -= 85;
		out.r = 0;
		out.g = WheelPos * 3;
		out.b = 255 - WheelPos * 3;
		return out;
	} else {
		WheelPos -= 170;
		out.r = WheelPos * 3;
		out.g = 255 - WheelPos * 3;
		out.b = 0;
		return out;
  }
}

esp_err_t pixel_test_init(void)
{

    pixel_channel_config_t* test_channel[PIXEL_CHANNEL_MAX];
	uint8_t number_of_channels = 8;
	uint32_t led_lengths[PIXEL_CHANNEL_MAX] =
	{
			[PIXEL_CHANNEL_0] = 175,
			[PIXEL_CHANNEL_1] = 175,
			[PIXEL_CHANNEL_2] = 175,
			[PIXEL_CHANNEL_3] = 175,
			[PIXEL_CHANNEL_4] = 175,
			[PIXEL_CHANNEL_5] = 175,
			[PIXEL_CHANNEL_6] = 175,
			[PIXEL_CHANNEL_7] = 175
	};

    for(uint8_t a = 0; a < number_of_channels; a++)
    {

    		test_channel[a] = pixel_generate_channel_conf((pixel_channel_t)a, led_lengths[a], PIXEL_WS2812B_V1);

		pixel_init_channel(test_channel[a]);
    }

    uint8_t color = 0;
    while (1){
	    	for(uint8_t a = 0; a < number_of_channels; a++)
	    	{
	    		/*Wait for semaphore to signal pixel data is able to be updated*/
//	    		xSemaphoreTake(test_channel[a]->xPixelSemaphoreData, portMAX_DELAY);

			for (uint32_t i=0; i<test_channel[a]->channel_length; i++) {


						test_channel[a]->pixel_data[i].r = Wheel(color).r;
						test_channel[a]->pixel_data[i].g = Wheel(color).g;
						test_channel[a]->pixel_data[i].b = Wheel(color).b;
			}
			/*Give semaphore so that the pixel data is able to be sent*/
//			xSemaphoreGive(test_channel[a]->xPixelSemaphoreData);

	    	}
	    	for(uint8_t a = 0; a < number_of_channels; a++)
	    	{
	    		pixel_update_data(test_channel[a]);
	    	}
	    	color++;
		vTaskDelay(10/portTICK_PERIOD_MS);




	}

	return ESP_OK;
}

void app_main(void)
{
    printf("Hello world!\n");

    /* Print chip information */
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    printf("This is ESP32 chip with %d CPU cores, WiFi%s%s, ",
            chip_info.cores,
            (chip_info.features & CHIP_FEATURE_BT) ? "/BT" : "",
            (chip_info.features & CHIP_FEATURE_BLE) ? "/BLE" : "");

    printf("silicon revision %d, ", chip_info.revision);

    printf("%dMB %s flash\n", spi_flash_get_chip_size() / (1024 * 1024),
            (chip_info.features & CHIP_FEATURE_EMB_FLASH) ? "embedded" : "external");

    printf("Starting\n");

	pixel_test_init();

	while(1)
	{
		vTaskDelay(100);
	}

}

