# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Dafne-Imaging Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import SimpleITK as sitk

DEFAULT_BIAS_CORRECTION_LEVELS = 8


def biascorrection(file_or_image, levels=DEFAULT_BIAS_CORRECTION_LEVELS, normalize=False):
    if type(file_or_image) == str:
        return biascorrection_file(file_or_image, levels)
    else:
        return biascorrection_image(file_or_image, levels)


def biascorrection_image(image, levels=DEFAULT_BIAS_CORRECTION_LEVELS, normalize=False):
    print('Bias correction 202401')
    MAX_GRAY_VALUE = 600
    if not type(image) == sitk.SimpleITK.Image:
        # normalize values
        image = image*MAX_GRAY_VALUE/image.max()
        image = sitk.GetImageFromArray(image)
        image = sitk.Cast(image, sitk.sitkFloat32)
    else:
        image = sitk.GetArrayFromImage(image)
        image = image * MAX_GRAY_VALUE / image.max()
        image = sitk.GetImageFromArray(image)
        image = sitk.Cast(image, sitk.sitkFloat32)

    maskImage = sitk.OtsuThreshold(image, 0, 1, 200)
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    numberFittingLevels = levels
    numberOfIteration = [50]
    corrector.SetMaximumNumberOfIterations(numberOfIteration * numberFittingLevels)
    output = corrector.Execute(image, maskImage)
    img2 = sitk.GetArrayFromImage(output)
    # normalize is zero or false
    if not normalize:
        return img2

    if normalize is True:
        mean = img2.mean()
        sd = img2.std()
        return (img2 - mean) / sd

    # normalize to a specific value
    if normalize > 0:
        return img2 * normalize / img2.max()

    # normalize is < 0: normalize to default value
    return img2 * MAX_GRAY_VALUE / img2.max()




def biascorrection_file(nifti_file, levels=DEFAULT_BIAS_CORRECTION_LEVELS, normalize=False):
    inputImage = sitk.ReadImage(nifti_file,sitk.sitkFloat32) 
    return biascorrection_image(inputImage, levels)
