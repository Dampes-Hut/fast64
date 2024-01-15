from .....utility import CData, indent
from ....oot_level_classes import OOTRoom, LightInfoStruct, LightInfoTypeEnum, LightParamsPointStruct
from .actor import getActorList
from .room_commands import getRoomCommandList


def getHeaderDefines(outRoom: OOTRoom, headerIndex: int):
    """Returns a string containing defines for actor and object lists lengths"""
    headerDefines = ""

    if len(outRoom.lightInfoList) > 0:
        headerDefines += (
            f"#define {outRoom.getLightInfoListLengthDefineName(headerIndex)} {len(outRoom.lightInfoList)}\n"
        )

    if len(outRoom.objectIDList) > 0:
        headerDefines += f"#define {outRoom.getObjectLengthDefineName(headerIndex)} {len(outRoom.objectIDList)}\n"

    if len(outRoom.actorList) > 0:
        headerDefines += f"#define {outRoom.getActorLengthDefineName(headerIndex)} {len(outRoom.actorList)}\n"

    return headerDefines


# Object List
def getObjectList(outRoom: OOTRoom, headerIndex: int):
    objectList = CData()
    declarationBase = f"s16 {outRoom.objectListName(headerIndex)}"

    # .h
    objectList.header = f"extern {declarationBase}[];\n"

    # .c
    objectList.source = (
        (f"{declarationBase}[{outRoom.getObjectLengthDefineName(headerIndex)}]" + " = {\n")
        + ",\n".join(indent + objectID for objectID in outRoom.objectIDList)
        + ",\n};\n\n"
    )

    return objectList


def lightInfoToC(li: LightInfoStruct):
    assert li.type in {LightInfoTypeEnum.LIGHT_POINT_GLOW, LightInfoTypeEnum.LIGHT_POINT_NOGLOW}
    lipp = li.params
    assert isinstance(lipp, LightParamsPointStruct)
    params_struct_name = "point"
    params_struct_c = (
        (", ".join(map(str, [lipp.x, lipp.y, lipp.z])) + ",\n")
        + ("{ " + ", ".join(map(str, lipp.color)) + " },\n")
        + ("0,\n")
        + (str(lipp.radius))
    )
    return (
        "{\n"
        + (indent + li.type.name + ",\n")
        + (
            (indent + f".params.{params_struct_name} = " + "{\n")
            + "\n".join(indent + indent + line for line in params_struct_c.splitlines())
            + "\n"
            + (indent + "}\n")
        )
        + "}"
    )


def getLightInfoList(outRoom: OOTRoom, headerIndex: int):
    lightInfoList = CData()
    declarationBase = f"LightInfo {outRoom.lightInfoListName(headerIndex)}"

    # .h
    lightInfoList.header = f"extern {declarationBase}[];\n"

    # .c
    lightInfoList.source = (
        (f"{declarationBase}[{outRoom.getLightInfoListLengthDefineName(headerIndex)}]" + " = {\n")
        + "".join(
            "\n".join(indent + line for line in lightInfoToC(li).splitlines()) + ",\n" for li in outRoom.lightInfoList
        )
        + "};\n\n"
    )

    return lightInfoList


# Room Header
def getRoomData(outRoom: OOTRoom):
    roomC = CData()

    roomHeaders: list[tuple["OOTRoom | None", str]] = [
        (outRoom.childNightHeader, "Child Night"),
        (outRoom.adultDayHeader, "Adult Day"),
        (outRoom.adultNightHeader, "Adult Night"),
    ]

    for i, csHeader in enumerate(outRoom.cutsceneHeaders):
        roomHeaders.append((csHeader, f"Cutscene No. {i + 1}"))

    declarationBase = f"SceneCmd* {outRoom.alternateHeadersName()}"

    # .h
    roomC.header = f"extern {declarationBase}[];\n"

    # .c
    altHeaderPtrList = (
        f"{declarationBase}[]"
        + " = {\n"
        + "\n".join(
            indent + f"{curHeader.roomName()}_header{i:02}," if curHeader is not None else indent + "NULL,"
            for i, (curHeader, headerDesc) in enumerate(roomHeaders, 1)
        )
        + "\n};\n\n"
    )

    roomHeaders.insert(0, (outRoom, "Child Day (Default)"))
    for i, (curHeader, headerDesc) in enumerate(roomHeaders):
        if curHeader is not None:
            roomC.source += "/**\n * " + f"Header {headerDesc}\n" + "*/\n"
            roomC.source += getHeaderDefines(curHeader, i)
            roomC.append(getRoomCommandList(curHeader, i))

            if i == 0 and outRoom.hasAlternateHeaders():
                roomC.source += altHeaderPtrList

            if len(curHeader.lightInfoList) > 0:
                roomC.append(getLightInfoList(curHeader, i))

            if len(curHeader.objectIDList) > 0:
                roomC.append(getObjectList(curHeader, i))

            if len(curHeader.actorList) > 0:
                roomC.append(getActorList(curHeader, i))

    return roomC
