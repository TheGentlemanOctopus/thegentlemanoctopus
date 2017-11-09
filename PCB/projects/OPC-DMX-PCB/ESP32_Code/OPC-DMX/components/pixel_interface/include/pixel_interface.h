/*
 * pixel_interface.h
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben Holden
 */

#ifndef COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_
#define COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_

#include "driver/rmt.h"


#define RMT_MEM_BLOCK_NUM 1 /* 1 block of data per channel */
#define RMT_MEM_BLOCK_SIZE 64/* For some reason the max it can do with loop around mode is 62... No idea why?? */

#define RMT_DIVIDER 2 /* Divide the RMT APB clock by this */
#define RMT_SPEED 12.5 /* APB Clock 1/80MHZ in nanoseconds */
#define RMT_CLK_DIVIDER (RMT_SPEED * RMT_DIVIDER)

#define PIXEL_BIT_MASK_INIT 0x00000001 /* mask used for determining if a bit is a 1 or 0 */
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
	PIXEL_WS2812_V1=0,
	PIXEL_WS2812B_V1,
	PIXEL_WS2812B_V2,
	PIXEL_WS2812B_V3,
	PIXEL_WS2813_V1,
	PIXEL_WS2813_V2,
	PIXEL_WS2813_V3,
	PIXEL_SK6812_V1,
	PIXEL_SK6812W_V1,
	PIXEL_NAME_MAX
} pixel_name_t;

typedef enum {
	PIXEL_BIT_lOW=0,
	PIXEL_BIT_HIGH,
	PIXEL_BIT_MAX
} pixel_bit_type;

/* Structure of pixel data, grbw backwards as neopixels are msb first */
typedef union {
	struct {
		uint8_t	w; /* White */
		uint8_t	b; /* Blue */
		uint8_t	r; /* Red */
		uint8_t g; /* Green */
	};

	uint32_t data;
} pixel_data_t;

/* Structure of pixels, for modularity between different manufacturers */
typedef struct {
	rmt_item32_t pixel_bit[PIXEL_BIT_MAX]; /* Store for the 1 & 0 and reset RMT data */
	uint8_t colour_num; /* Number of colours in pixel eg, 3 for rgb 4 for rgbw */
	uint16_t reset :15;
} pixel_type_t;

/* Structure of counters used to convert from pixel data to RMT*/
typedef struct {
	uint32_t rmt_counter; /* Counter for position in the RMT memory block */
	uint8_t rmt_block_max; /* Maximum the RMT block can get to before break needs to happen */
	uint32_t pixel_counter; /* Counter for individual pixels in channel */
	uint32_t bit_counter; /* Counter for individual bits in the temp pixel data */
	uint32_t temp_pixel_data; /* Temporary store for the pixel to be sent */
} pixel_counter_t;

/* Structure of an individual pixel channel */
typedef struct {
	pixel_channel_t pixel_channel; /* Name of pixel channel*/
	rmt_channel_t rmt_channel; /* RMT channel to use for outputting the pixel data*/
	rmt_item32_t* rmt_mem_block; /* Pointer to the memory block that RMT will use */
	gpio_num_t gpio_output_pin; /* Pin that the data will be output on */
	uint32_t channel_length; /* Number of pixels on channel*/
	pixel_data_t* pixel_data; /* Pointer to pixel data */
	pixel_type_t pixel_type; /* Pixel types, eg WS2812 */
	pixel_counter_t counters; /* Counters for the pixel to RMT conversions */
} pixel_channel_config_t;

/* Definitions of pixels */
extern const pixel_type_t pixel_type_lookup[PIXEL_NAME_MAX];

void pixel_init_channel(pixel_channel_config_t* channel);
void pixel_init_rmt_channel(pixel_channel_config_t* channel);
void pixel_create_data_buffer(pixel_channel_config_t* channel);
void pixel_delete_data_buffer(pixel_channel_config_t* channel);
void pixel_start_channel(pixel_channel_config_t* channel);
void pixel_stop_channel(pixel_channel_config_t* channel);
void pixel_send_data(pixel_channel_config_t* channel);

static IRAM_ATTR void pixel_intr_handler(void* arg);

#endif /* COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_ */
