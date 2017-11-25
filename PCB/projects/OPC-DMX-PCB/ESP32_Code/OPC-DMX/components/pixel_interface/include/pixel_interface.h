/*
 * pixel_interface.h
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben Holden
 *      The Gentleman Octopus Ltd
 *
 */

#ifndef COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_
#define COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_

#include "driver/rmt.h"


#define RMT_MEM_BLOCK_NUM 1 /* 1 block of data per channel */
#define RMT_MEM_BLOCK_SIZE 64 /* There are 64 32bit addresses for each rmt channel*/

#define RMT_DIVIDER 2 /* Divide the RMT APB clock by this */
#define RMT_SPEED 12.5 /* APB Clock 1/80MHZ in nanoseconds */
#define RMT_CLK_DIVIDER (RMT_SPEED * RMT_DIVIDER)

#define PIXEL_BIT_MASK 0x00000001 /* mask used for determining if a bit is a 1 or 0 */

#define RMT_BUFFER_FULL 0xFF
/**
 * Enums
 */

/**
 * @brief Pixel Channel types
 */
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

/**
 * @brief Pixel Name type
 * Used for storing the names of different pixels.
 */
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

/**
 * @brief Pixel Bit types
 */
typedef enum {
	PIXEL_BIT_lOW=0,
	PIXEL_BIT_HIGH,
	PIXEL_BIT_MAX
} pixel_bit_type;

/**
 * Structures
 */

/**
 * @brief Pixel Data types
 * Structure of pixel data, grbw backwards as neopixels are msb first
 */
typedef union {
	struct {
		uint8_t	w; /* White */
		uint8_t	b; /* Blue */
		uint8_t	r; /* Red */
		uint8_t g; /* Green */
	};

	uint32_t data;
} pixel_data_t;

/**
 * @brief Pixel type
 * Structure of pixels, for modularity between different manufacturers.
 * Stores the timings for RMT, number of colours and how long the reset pulse is.
 */
typedef struct {
	rmt_item32_t pixel_bit[PIXEL_BIT_MAX]; /* Store for the 1 & 0 and reset RMT data */
	uint8_t colour_num; /* Number of colours in pixel eg, 3 for rgb 4 for rgbw */
	uint16_t reset :15;
} pixel_type_t;

/**
 * @brief Pixel Counter Type
 * Structure of counters used to convert from pixel data to RMT
 * */
typedef struct {
	uint32_t rmt_counter; /* Counter for position in the RMT memory block */
	uint8_t rmt_block_max; /* Maximum the RMT block can get to before break needs to happen */
	uint32_t pixel_counter; /* Counter for individual pixels in channel */
	uint32_t bit_counter; /* Counter for individual bits in the temp pixel data */
	uint32_t temp_pixel_data; /* Temporary store for the pixel to be sent */
} pixel_counter_t;

/**
 * @brief Pixel Channel Config Type
 * Structure of an individual pixel channel.
 * Contains everything needed to initialise and send out pixel channels.
 * Use 1 per pixel channel.
 */
typedef struct {
	pixel_channel_t pixel_channel; /* Name of pixel channel 0-7*/
	rmt_channel_t rmt_channel; /* RMT channel to use for outputting the pixel data 0-7 normally same as pixel_channel number*/
	rmt_item32_t* rmt_mem_block; /* Pointer to the memory block that RMT will use */
	gpio_num_t gpio_output_pin; /* Pin that the data will be output on */
	uint32_t channel_length; /* Number of pixels on channel*/
	pixel_data_t* pixel_data; /* Pointer to pixel data */
	pixel_type_t pixel_type; /* Pixel types, eg WS2812 */
	pixel_counter_t counters; /* Counters for the pixel to RMT conversions */
} pixel_channel_config_t;

/**
 * Public Variables
 */

/**
 * @brief Pixel Type Lookup
 * Definitions of pixels saved in an array of pixel_type_t to be,
 * copied across on pixel channel initialisation, depending on the user requirements.
 */
extern const pixel_type_t pixel_type_lookup[PIXEL_NAME_MAX];

/**
 * Public Functions
 */

/**
 * @brief Pixel Generate Channel Conf
 * Allocates memory for and sets up a pixel_channel_config_t structure with the parameters sent
 *
 * @param pixel_channel Number of the pixel channel to generate (0-7)
 *
 * @param channel_length Number of pixels in channel
 *
 * @param pixel_type Type of pixels to be used on channel
 *
 * @return Pointer to the generated structure
 */
pixel_channel_config_t* pixel_generate_channel_conf(pixel_channel_t pixel_channel, uint32_t channel_length, pixel_name_t pixel_type);

/**
 * @brief Pixel Init Channel
 * Initialises the required RMT channel
 * and creates the data buffer for RGB data
 *
 * @param channel Pixel channel config structure
 */
void pixel_init_channel(pixel_channel_config_t* channel);

/**
 * @brief Pixel Init RMT Channel
 * Initialises the required RMT channel
 * in a way that it can be used to send out pixel data
 *
 * @param channel Pixel channel config structure
 */
void pixel_init_rmt_channel(pixel_channel_config_t* channel);

/**
 * @brief Pixel Create Data Buffer
 * Creates a data buffer the desired size and adds the pointer to the channel config
 *
 * @param channel Pixel channel config structure
 */
void pixel_create_data_buffer(pixel_channel_config_t* channel);

/**
 * @brief Pixel Delete Data Buffer
 * Frees the memory and NULLs the pointer for the pixel data
 *
 * @param channel Pixel channel config structure
 */
void pixel_delete_data_buffer(pixel_channel_config_t* channel);

/**
 * @brief Pixel Start Channel
 * Starts sending out pixel_data on a channel continuously.
 * Once started it will send out the data in channel.pixel_data forever.
 * Change the channel.pixel_data and it will be sent out on the next iteration.
 *
 * @note When this is called, it sets up interrupts that could interfere with
 * other time critical code. Preferably have all the pixel sending happen on one core.
 * Using the other for the RGB data generation and other things.
 *
 * @param channel Pixel channel config structure
 */
void pixel_start_channel(pixel_channel_config_t* channel);

/**
 * @brief Pixel Stop Channel
 * Stops the pixel channel sending out data.
 *
 * @param channel Pixel channel config structure
 */
void pixel_stop_channel(pixel_channel_config_t* channel);

/**
 * @brief Pixel Send Data
 * Converts the channel.pixel_data into RMT 1 wire data
 * that will be sent out on the physical pins.
 *
 * @note This is called in pixel_start_channel
 *
 * @param channel Pixel channel config structure
 */
void pixel_send_data(pixel_channel_config_t* channel);
void pixel_send_data_multi_channel(pixel_channel_config_t** channels, uint8_t* index_queue, uint8_t index_count);
bool pixel_convert_data(pixel_channel_config_t* channel);
/**
 * @brief Pixel Intr Handler
 * Deals with the RMT interrupts and figures out what channel to fill next.
 * This should be a high priority interrupt to keep the pixels in sync
 */
IRAM_ATTR void pixel_intr_handler(void* arg);

#endif /* COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_ */
