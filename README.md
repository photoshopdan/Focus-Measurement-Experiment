# Focus Measurement Experiment

I was tasked with finding ways to improve the way my client rejects out-of-focus school photography images. I had previously provided them with a solution which made use of Amazon Web Services' Rekognition service, however the accuracy of their sharpness metric was not high enough to reliably separate in-focus from blurry images.

I proposed a method which performs a sharpness measurement only on the eye region, in an effort to normalise the image content across images and remove the bias that can cause sharpness measurements to vary.

The purpose of this experiment is to compare a selection of sharpness measurement methods to find which one is most effective.