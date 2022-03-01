#ifndef SHARPNESS_H
#define SHARPNESS_H

#include <vector>
#include <cstdint>

struct Point2D
{
    int x;
    int y;
};

double eye_sharpness(
    const std::vector<std::vector<std::uint8_t>>& image,
    const std::vector<Point2D>& eyes,
    int window_size=100);

#endif
