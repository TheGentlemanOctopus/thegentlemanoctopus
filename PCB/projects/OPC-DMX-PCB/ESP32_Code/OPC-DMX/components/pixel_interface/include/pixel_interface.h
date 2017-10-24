/*
 * pixel_interface.h
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben Holden
 */

#ifndef COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_
#define COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_

#include "driver/rmt.h"

#define RMT_DIVIDER 4 /* Divide the RMT APB clock by this */
#define RMT_MEM_BLOCK_NUM 1 /* 1 block of data per channel */
#define RMT_MEM_BLOCK_SIZE 32 /* 32x32bit data per block (fill half a block at a time) */

typedef enum {
    PIXEL_CHANNEL_0=0, /*!< Pixel Channel0 */
    PIXEL_CHANNEL_1,   /*!< Pixel Channel1 */
    PIXEL_CHANNEL_3,   /*!< Pixel Channel3 */
    PIXEL_CHANNEL_4,   /*!< Pixel Channel4 */
    PIXEL_CHANNEL_2,   /*!< Pixel Channel2 */
    PIXEL_CHANNEL_5,   /*!< Pixel Channel5 */
    PIXEL_CHANNEL_6,   /*!< Pixel Channel6 */
    PIXEL_CHANNEL_7,   /*!< Pixel Channel7 */
    PIXEL_CHANNEL_MAX
} pixel_channel_t;

typedef enum {
	LED_WS2812_V1=0,
	LED_WS2812B_V1,
	LED_WS2812B_V2,
	LED_WS2812B_V3,
	LED_WS2813_V1,
	LED_WS2813_V2,
	LED_WS2813_V3,
	LED_SK6812_V1,
	LED_SK6812W_V1
} pixel_type_t;

typedef union {
	struct {
		uint8_t g;
		uint8_t	r;
		uint8_t	b;
		uint8_t	w;
	};

	uint32_t data;
} pixel_data_t;


typedef struct {
	pixel_channel_t pixel_channel; /* Name of pixel channel*/
	rmt_channel_t rmt_channel; /* RMT channel to use for outputting the pixel data*/
	rmt_item32_t* rmt_data; /* Pointer to the data that RMT will use */
	gpio_num_t gpio_output_pin; /* Pin that the data will be output on */
	uint32_t channel_length; /* Number of pixels on channel*/
	pixel_data_t* pixel_data; /* Pointer to pixel data */
	pixel_type_t pixel_type; /* Pixel types, eg WS2812 */
} pixel_channel_config_t;




void pixel_init_rmt_channel(pixel_channel_config_t* channel);
void pixel_create_data_buffer(pixel_channel_config_t* channel);
void pixel_delete_data_buffer(pixel_channel_config_t* channel);
void pixel_start_channel(pixel_channel_config_t* channel);
void pixel_stop_channel(pixel_channel_config_t* channel);
void pixel_send_data(pixel_channel_config_t* channel);

#endif /* COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_ */
