
def block_parser(block: str) -> str:
    if block == "bee_nest_honey":
        output = "bee_nest[honey_level=5]"
    elif block == "beehive_honey":
        output = "beehive[honey_level=5]"
    elif block == "blast_furnace_on":
        output = "blast_furnace[lit=true]"
    elif block == "chorus_flower_dead":
        output = "chorus_flower[age=5]"
    elif block == "daylight_detector_inverted":
        output = "daylight_detector[inverted=true]"
    elif block == "dispenser":
        output = "dispenser[facing=up]"
    elif block == "dropper_vertical":
        output = "dropper[facing=up]"
    elif block == "farmland":
        output = "farmland"
    elif block == "farmland_moist":
        output = "farmland[moisture=7]"
    elif block == "furnace_on":
        output = "furnace[lit=true]"
    elif block == "jigsaw_lock":
        output = "jigsaw[orientation=up_north]"
    elif block == "lava_still":
        output = "lava"
    elif block == "mushroom_block_inside":
        output = "mushroom_stem[up=false,down=false,east=false,west=false,north=false,south=false]"
    elif block == "piston_sticky":
        output = "sticky_piston"
    elif block == "redstone_lamp_on":
        output = "redstone_lamp[lit=true]"
    elif block == "respawn_anchor_lit":
        output = "respawn_anchor[charges=4]"
    elif block == "sculk_shrieker_enabled":
        output = "sculk_shrieker[can_summon=true]"
    elif block == "smoker_on":
        output = "smoker[lit=true]"
    elif block == "structure_block_load":
        output = "structure_block"
    elif block == "structure_block_data":
        output = "structure_block[mode=data]"
    elif block == "structure_block_corner":
        output = "structure_block[mode=corner]"
    elif block == "structure_block_load":
        output = "structure_block[mode=load]"
    elif block == "structure_block_save":
        output = "structure_block[mode=save]"
    elif block == "magma":
        output = "magma_block"
    elif block == "dried_kelp":
        output = "dried_kelp_block"
    else:
        output = block

    output = "minecraft:" + output
    return output
