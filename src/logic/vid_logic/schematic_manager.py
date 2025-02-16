# TODO
# Vertical/Horizontal orientation of the schematic
# Perhaps commands in one area, frames in another
# A set amount of frame peed, 20, 10, 5, 4, 2, 1
# For a frame speed, the user decides if the video is slowed to show all frames
# Or frame are skipped to match relative speed
# Commands or no commands(Obviously, no redstone mechanism, orrrrr maybeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee)
# Nah too hard (Maybe black and white(as lamps), and as rom instead?)


import os

from mcschematic import MCSchematic

from src.path_manager.pather import resource_path
import mcschematic
assets_path = resource_path(f"../../../assets/cache/")
testing_vid_processed_folder = os.path.normpath(os.path.join(assets_path, "./img_process_cache/"))

# TODO: DIRECTIONS
def make_final_schematic(processed_folder:str, output: str, direction:str = "East"):
    print(processed_folder)
    all_files = os.listdir(processed_folder)
    num_list = [int(x.split(".")[0]) for x in all_files if not "out" in x]
    num_list.sort()
    all_schematics = [mcschematic.MCSchematic(processed_folder+f"\\{file}.schem") for file in num_list]
    final_schematic = mcschematic.MCSchematic()
    for i,schem in enumerate(all_schematics):
        final_schematic.placeSchematic(schem, (0,0,3*i))



    head, tail = os.path.split(output)
    tail = tail.split(".")[0]
    final_schematic.save(head, tail, mcschematic.Version.JE_1_20_1)


if __name__ == "__main__":
    make_final_schematic(testing_vid_processed_folder, testing_vid_processed_folder+"/out.schem")