## Focus Measurement Experiment

I was tasked with finding ways to improve the way my client rejects out-of-focus school photography images. I had previously provided them with a solution which made use of Amazon Web Services' Rekognition service, however the accuracy of their sharpness metric was not high enough to reliably separate in-focus from blurry images.

I proposed a method which performs a sharpness measurement only on the eye region, in an effort to normalise the image content across images and remove the bias that can cause sharpness measurements to vary.

The purpose of this experiment is to compare a selection of eye-centered sharpness measurement methods to find which one is most effective. The [results](https://github.com/photoshopdan/Focus-Measurement-Experiment/blob/main/Focus%20Measurement%20Experiment.pdf) illustrate the problems with the AWS method and demonstrate two metrics which show better performance. I wrote two [scripts](https://github.com/photoshopdan/Focus-Measurement-Experiment/tree/main/scripts) which performed the data collection and presentation. [Histograms](https://github.com/photoshopdan/Focus-Measurement-Experiment/tree/main/example) and box plots were produced, however I chose to present only the box plots as they are far more readable.

Laplacian Variance was chosen as the new method due to it's accuracy and speed. An [implementation](https://github.com/photoshopdan/Focus-Measurement-Experiment/tree/main/src). of the final method was incorporated into the existing face analysis software.