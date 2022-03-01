#include "sharpness.hpp"
#include <vector>
#include <cstdint>
#include <stdexcept>
#include <numeric>
#include <algorithm>

using namespace std;

// Takes a single channel, downscaled image and a vector of eye coordinates.
// Returns a sharpness value.
double eye_sharpness(
	const vector<vector<uint8_t>>& image,
    const vector<Point2D>& eyes,
	int window_size)
{
    int image_width{ static_cast<int>(image[0].size()) };
    int image_height{ static_cast<int>(image.size()) };

	// Ensure window size is sensible. Default argument should be preferred.
    if (window_size < 8)
        throw runtime_error("Window too small");
    // Ensure image vector is larger than window size.
	if (image_width < window_size || image_height < window_size)
		throw runtime_error("Image is smaller than the window size");
    // Ensure individual has one or more eyes.
    if (eyes.empty())
        throw runtime_error("One or more eye coordinates required");

    double laplacian_var{ 0.0 };

    // Iterate over all eyes, adding to the sharpness result.
    for (auto eye{ eyes.begin() }; eye != eyes.end(); ++eye)
    {
        // Calculate window coordinates. Odd window sizes are rounded down.
        // 1 is subtracted because otherwise the 3x3 convolution would use
        // pixels outside of the window.
        int window_size_half{ window_size / 2 - 1 };
        int window_top{ eye->y - window_size_half };
        int window_bottom{ eye->y + window_size_half };
        int window_left{ eye->x - window_size_half };
        int window_right{ eye->x + window_size_half };

        // If the window protrudes outside of frame, slide it back into frame.
        if (window_top < 0)
        {
            int shift{ window_top - 1 };
            window_top -= shift;
            window_bottom -= shift;
        }
        else if (window_bottom > image_height)
        {
            int shift{ window_bottom - image_height + 1 };
            window_bottom -= shift;
            window_top -= shift;
        }
        if (window_left < 0)
        {
            int shift{ window_left - 1 };
            window_left -= shift;
            window_right -= shift;
        }
        else if (window_right > image_width)
        {
            int shift{ window_right - image_width + 1 };
            window_right -= shift;
            window_left -= shift;
        }

        // Set up kernel and empty vector to hold result of convolution.
        constexpr int laplace_kernel[9]{ 0, 1, 0, 1, -4, 1, 0, 1, 0 };
        vector<int> laplacian{};
        laplacian.reserve(window_size_half * 2 * window_size_half * 2);

        int counter{ 0 };
        int temp{ 0 };

        // Iterate over each pixel.
        for (int y{ window_top }; y < window_bottom; y++)
        {
            for (int x{ window_left }; x < window_right; x++)
            {
                // On each pixel, iterate over the kernel area.
                for (int i{ y - 1 }; i <= y + 1; i++)
                {
                    for (int j{ x - 1 }; j <= x + 1; j++)
                    {
                        // Add to the weighted sum.
                        temp += image[i][j] * laplace_kernel[counter];
                        counter++;
                    }
                }
                // Store the weighted sum of each pixel and reset accumulators.
                laplacian.push_back(temp);
                temp = 0;
                counter = 0;
            }
        }

        // Compute the sum and mean of the laplacian.
        double laplacian_sum{ reduce(
            laplacian.begin(), laplacian.end(), 0.0) };
        double laplacian_mean{ laplacian_sum / laplacian.size() };
        // Collect the differences from the mean.
        vector<double> diff(laplacian.size());
        transform(laplacian.begin(), laplacian.end(), diff.begin(),
            [laplacian_mean](double x) { return x - laplacian_mean; });
        // Sum the squared deviation from the mean.
        double sq_sum = inner_product(
            diff.begin(), diff.end(), diff.begin(), 0.0);
        // Return the variance.
        laplacian_var += sq_sum / laplacian.size();
    }

    // Return the mean sharpness value across all eyes.
	return laplacian_var / eyes.size();
}
