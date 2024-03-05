import src.ui_manager.PySimpleGUI as sg


def manage_popups(event):
    if event in ["-Average_Colour_Popup-", "-Vid_Average_Colour_Popup-"]:
        sg.popup_scrolled(
            """
            Average Color These are the pre-computed color averages of each minecraft block, in different ways \n
            -   Linear Average\n
                    The original average color list. It uses the arithmetic mean of all pixels of a minecraft block\n\n
            -   Root Mean Square Average\n
                    It is said in a legend once forgotten,
                    that rgb should be squared before taking the arithmetic mean
                    as whats shown to the world had been previously rooted\n\n
            -   HSL / HSV average\n
                    Converted rgb to hsl, before taking that average, Might be better idk\n\n
            -   Lab Average\n
                    'L*a*b*', referred to as lab, is the holy grail of color spaces or something, as it is supposed to based on human perception\n\n
            -   Dominant color\n
                    The most dominant color in the block is used here\n\n
            
            Note, i dont think there is any 'better' choice here\n
            You should choose whichever look the best/has best outcome for what you want
            """,
            background_color="#2a2b2c",
            title="Average Colour In Detailed",
            text_color="#FFFFFF",
            size=(130, 30)
        )

    if event in ["-Color_Difference_Popup-", "-Vid_Color_Difference_Popup-"]:
        sg.popup_scrolled(
            """
            This setting changes how the color values of each pixel is compared to the averaged minecraft block\n
            -   Absolute Difference\n
                    Adds up the absolute differences between the rgb values. This is theoretically the fastest\n\n
            -   Euclidean Difference\n
                    Very similar to absolute differences, but adds up the square of the differences between the rgb values\n\n
            -   Weighted Euclidean\n
                    Same as euclidean difference, but red, green and blue are weighted somewhat to match our eye's perception\n\n
            -   Redmean Difference\n
                    Similar to weighted euclidean, but is smoother in its working\n\n
            -   CIE76 DelE\n
                    Theoretically matches the color difference like our eyes the most, as compared to others
                    as it is based on a more human perception related color space
                    It is also much slower than the others\n\n

            Note, i dont think there is any 'better' choice here either\n
            You should choose whichever look the best/has best outcome for what you want
            """,
            background_color="#2a2b2c",
            title="Color Difference",
            text_color="#FFFFFF",
            size=(130, 30)
        )
