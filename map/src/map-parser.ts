export interface RobotMapFormat {
    format_version: "3.5.1";
    debug_file_header: {
        robot_name: string;
        blid: any[];
    };
    maps: RobotMap[];
}

export type RobotGeometryType = "multipoint2d"
    | "pose2dconcise_event"
    | "multipolygon2d"
    | "polygon"
    | "multilinestring"
    | "linestring";

export interface RobotGeometry {
    type: RobotGeometryType;
}

export interface RobotGeometryPolygon extends RobotGeometry {
    type: "polygon";
    ids: string[][];
}

export interface RobotGeometryLinestring extends RobotGeometry {
    type: "linestring";
    ids: string[];
}

export type RobotGeometryUnion = RobotGeometryPolygon
    | RobotGeometryLinestring;

export type CoordinateMultipoint2d = [number, number];

export interface RobotMapLayerCoverage {
    layer_type: "coverage";
    geometry: {
        point_area: [
            number,
            number,
        ],
        type: RobotGeometryType;
        coordinates: CoordinateMultipoint2d[];
    };
    features: any[];
}

export interface RobotMapLayerEscapeEvents {
    layer_type: "escape_events";
    geometry: {
        type: RobotGeometryType;
        list: any;
    };
}

export interface RobotMapLayerDirt {
    layer_type: "dirt";
    geometry: {
        point_area: [
            number,
            number,
        ],
        type: RobotGeometryType;
        coordinates: CoordinateMultipoint2d[];
    };
    features: any[];
}

export interface RobotMapLayerFrontier {
    layer_type: "frontiers";
    geometry: {
        type: RobotGeometryType;
        ids: string[][];
    };
    features: any[];
}

export type CoordinateCoveragePoly = any;

export interface RobotMapLayerCoveragePoly {
    layer_type: "coverage_poly";
    geometry: {
        type: RobotGeometryType;
        coordinates: CoordinateCoveragePoly[];
    };
    features: any[];
}

export interface RobotMapLayerClutter {
    layer_type: "clutter";
    geometry: {
        type: RobotGeometryType;
        coordinates: CoordinateCoveragePoly[];
    };
}

export type RobotMapLayer = RobotMapLayerCoverage
    | RobotMapLayerEscapeEvents
    | RobotMapLayerDirt
    | RobotMapLayerCoveragePoly
    | RobotMapLayerFrontier
    | RobotMapLayerClutter;

export type Point2d = [number, number];

export interface RobotPoint2d {
    id: string;
    coordinates: Point2d;
}

export interface RobotDevice {
}

export type RobotRegionType = "living_room" | "kitchen" | "foyer" | "bedroom" | "bathroom" | "custom";

export interface RobotRegion {
    region_type: RobotRegionType;
    geometry: RobotGeometryPolygon;
    id: string;
    name: string;
}

export interface RobotMapHeader {
    name: string;
    learning_percentage: number;
    version: string;
    create_time: number;
    user_orientation_rad: number;
    resolution: number;
    id: string;
    [key: string]: string | number;
}

export interface RobotKeepOutZones {

}

export interface RobotDoor {
    unhinged_start: boolean;
    geometry: RobotGeometryLinestring;
    region2: string;
    region1: string;
    unhinged_end: boolean;
    id: string;
}

export interface RobotTypePose {

}

export type RobotBorderFreeType = "free";
export interface RobotBorder {
    geometry: RobotGeometryPolygon;
    id: string;
    free_type: RobotBorderFreeType;
}

export interface RobotPose2d {
    ori_rad: number;
    id: string;
    coordinates: Point2d;
}

export interface RobotMap {
    layers: RobotMapLayer[];
    points2d: RobotPoint2d[];
    devices: RobotDevice[];
    regions: RobotRegion[];
    map_header: RobotMapHeader;
    keepoutzones: RobotKeepOutZones[];
    doors: RobotDoor[];
    typed_poses: RobotTypePose;
    borders: RobotBorder[];
    poses2d: RobotPose2d[];
}

export interface RobotPoints2dMap { [key: string]: Point2d; }

export interface RobotMapParsedMap {
    points2d: RobotPoints2dMap;
    mapIndex: number;
}
export interface RobotMapParsed {
    robotMap: RobotMapFormat;
    maps: RobotMapParsedMap[];
}

export const parseMap = async (mapString: string): Promise<RobotMapFormat | Error> => {
    const json = JSON.parse(mapString);
    if (json instanceof Error) {
        return json;
    }
    return json as RobotMapFormat;
};
