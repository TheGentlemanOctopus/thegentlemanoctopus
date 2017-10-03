/*
 * pixel_interface.h
 *
 *  Created on: 20 Sep 2017
 *      Author: Ben Holden
 */

#ifndef COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_
#define COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_

#include "driver/rmt.h"

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

typedef struct {
	pixel_channel_t pixel_channel; /* Name of pixel channel*/
	rmt_channel_t RMT_channel; /* RMT channel to use for outputting the pixel data*/
	gpio_num_t GPIO_output_pin; /* Pin that the data will be output on */
	uint32_t channel_length; /* Number of pixels on channel*/



} pixel_channel_config_t;

typedef struct {

} pixel_data_t;


void init_pixel_channels(void);

#endif /* COMPONENTS_PIXEL_INTERFACE_INCLUDE_PIXEL_INTERFACE_H_ */
