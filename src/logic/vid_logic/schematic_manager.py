# TODO
# Vertical/Horizontal orientation of the schematic
# Perhaps commands in one area, frames in another
# A set amount of frame peed, 20, 10, 5, 4, 2, 1
# For a frame speed, the user decides if the video is slowed to show all frames
# Or frame are skipped to match relative speed
# Commands or no commands(Obviously, no redstone mechanism, orrrrr maybeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee)
# Nah too hard (Maybe black and white(as lamps), and as rom instead?)


import os
import logging

from src.logger import configure_logging, configure_logging_only_console

configure_logging_only_console()

logger = logging.getLogger(__name__)

from src.path_manager.pather import resource_path
import mcschematic
assets_path = resource_path(f"../../../assets/cache/")
testing_vid_processed_folder = os.path.normpath(os.path.join(assets_path, "./img_process_cache/"))

# TODO: DIRECTIONS
def make_final_schematic(processed_folder:str, output: str, details: dict, direction:str = "East"):
    logger.info(f"Processed folder: {processed_folder}")
    all_files = os.listdir(processed_folder)
    num_list = [int(x.split(".")[0]) for x in all_files if not "out" in x]
    num_list.sort()
    logger.info(f"Number of frames: {len(num_list)}")

    frame_size = mcschematic.MCSchematic(processed_folder+f"\\{num_list[0]}.schem")._structure.getBounds()
    logger.info(f"Frame Size: {frame_size}")
    final_schematic = mcschematic.MCSchematic()
    frame_wait_scale = round(20/details['frame_rate'])

    five_percent_detector = round(len(all_files)/20)
    for i,schem_number in enumerate(num_list):
        frame = mcschematic.MCSchematic(processed_folder+f"\\{schem_number}.schem")
        if i%five_percent_detector == 0:
            logger.info(f"Completed {i/len(all_files)*100}%")
        final_schematic.placeSchematic(frame, (0,0,i))
        # Putting this at 1,0,0| not -1,0,0 because all schematics atm have a negative bounds
        # TODO: MAKE A SCOREBOARD frame_number, and we iterate 0 to highest of fake player #Frame_Number
        final_schematic.setBlock((1,frame_size[0][1],i),
                                 blockData='repeating_command_block[facing=up]{auto:1b,Command:"'
                                           + f'execute if score #Frame_Number frame_number matches {i*frame_wait_scale} run '+
                                           f"clone ~{frame_size[0][0]-1} ~{-frame_size[0][1]} ~{0} ~{frame_size[1][0]-1} ~{-frame_size[1][1]} ~{0} ~{frame_size[0][0]-1} ~{0} ~{-2-i}"+'"}')
        # To save memory
        del frame
    final_schematic.setBlock((1,frame_size[0][1]+1,num_list[-1]-1), blockData='chain_command_block[conditional=true,facing=up]{auto:1b,Command:"scoreboard players set #Frame_Number frame_number -2"}')



    head, tail = os.path.split(output)
    tail = tail.split(".")[0]
    final_schematic.save(head, tail, mcschematic.Version.JE_1_20_1)


if __name__ == "__main__":
    make_final_schematic(testing_vid_processed_folder, testing_vid_processed_folder+"/out.schem", details={'frame_rate': 20})