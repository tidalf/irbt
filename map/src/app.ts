
import d3 from "d3";

// Static map data for testing
import { robotMapData } from "./data";
export { robotMapData };

import {
    Point2d,
    RobotGeometryLinestring,
    RobotGeometryPolygon,
    RobotGeometryUnion,
    RobotMap,
    RobotMapFormat,
    RobotMapParsed,
    RobotMapParsedMap,
    RobotPoint2d,
    RobotPoints2dMap,
    RobotRegionType,
} from "./map-parser";

type SvgSelection = d3.Selection<SVGSVGElement, unknown, HTMLElement, any>;

type RegionColorMap = { [type in RobotRegionType]: string };

interface Color {
    stroke?: string;
    strokeWidth?: number;
    fill: string;
}

const robotMapRegionColor: RegionColorMap = {
    bathroom: "grey",
    bedroom: "cyan",
    custom: "yellow",
    foyer: "blue",
    kitchen: "red",
    living_room: "green",
};

const setMapHeader = (selector: string, data: RobotMapParsed, mapIndex: number) => {
    const map_header = data.robotMap.maps[mapIndex].map_header;
    const root = document.querySelector(selector) as HTMLElement;
    Object.keys(map_header).map((key: string) => {
        const div = document.createElement("div");
        div.innerHTML = "<b>${key}</b>: ${map_header[key]}";
        root.appendChild(div);
    });
};

const myScale = d3.scaleLinear()
    .domain([-10, 10])
    .range([0, 800]);

const lineFunction = d3.line()
    .x((d: Point2d) => myScale(-d[0]))
    .y((d: Point2d) => myScale(d[1]))
    .curve(d3.curveLinear);

const getBoundingBox = (selection: SvgSelection) => {
    const element = selection.node();
    if (!element) {
        throw new Error("NullNodeError");
    }
    const bbox = element.getBBox();
    return {
        bbox,
        center: {
            x: bbox.x + bbox.width / 2,
            y: bbox.y + bbox.height / 2,
        },
        element,
    };
};

const drawRect = (svg: SvgSelection, rect: DOMRect, color: Color) => {
    return svg.append("rect")
        .attr("x", rect.x)
        .attr("y", rect.y)
        .attr("width", rect.width)
        .attr("height", rect.height)
        .attr("fill", color.fill);
};

const drawGeometryPolygon = (
    map: RobotMapParsedMap,
    svg: SvgSelection,
    geometry: RobotGeometryPolygon,
    color: Color,
) => {
    const points2d = map.points2d;
    const lineData: Point2d[] = [];
    geometry.ids.map((polygon: string[]) => {
        polygon.map((id) => {
            lineData.push(points2d[id]);
        });
    });
    const path = svg.append("path")
        .attr("d", lineFunction(lineData) as any)
        .attr("stroke", color.stroke ? color.stroke : "black")
        .attr("stroke-width", color.strokeWidth ? color.strokeWidth : 1)
        .attr("fill", color.fill);
    return path;
};

const drawGeometryLinestring = (
    map: RobotMapParsedMap,
    svg: SvgSelection,
    geometry: RobotGeometryLinestring,
    color: Color,
) => {
    const points2d = map.points2d;
    const lineData: Point2d[] = [];
    geometry.ids.map((id: string) => {
        lineData.push(points2d[id]);
    });
    const path = svg.append("path")
        .attr("d", lineFunction(lineData) as any)
        .attr("stroke", color.stroke ? color.stroke : "black")
        .attr("stroke-width", color.strokeWidth ? color.strokeWidth : 1)
        .attr("fill", color.fill);
    return path;
};

const drawPoint2d = (
    svg: SvgSelection,
    point2d: Point2d,
    color: Color,
) => {
    svg.append("circle")
        .attr("cx", point2d[0])
        .attr("cy", point2d[1])
        .attr("stroke", color.stroke ? color.stroke : "black")
        .attr("r", color.strokeWidth ? color.strokeWidth : 1)
        .attr("fill", color.fill);
};

const drawGeometry = (data: RobotMapParsedMap, svg: SvgSelection, geometry: RobotGeometryUnion, color: Color) => {
    switch (geometry.type) {
        case "polygon":
            return drawGeometryPolygon(data, svg, geometry, color);
        case "linestring":
            return drawGeometryLinestring(data, svg, geometry, color);
        default:
            throw new Error(`UnknownGeometry`);
    }
};

const drawMapRegions = (data: RobotMapParsed, mapIndex = 0, svg: SvgSelection) => {
    const map = data.robotMap.maps[mapIndex];
    map.regions.map((region) => {
        const path = drawGeometry(data.maps[mapIndex], svg, region.geometry, {
            fill: robotMapRegionColor[region.region_type],
            stroke: "blue",
        });
        const bbox = getBoundingBox(path as any); // @todo dirty typing
        const drawedBox = drawRect(svg, bbox.bbox, { fill: "black", stroke: "white" });
        drawedBox.lower();
        svg.append("text")
            .attr("x", () => bbox.center.x)
            .attr("y", () => bbox.center.y)
            .text(() => `${region.name}`)
            .attr("font-family", "Luminary")
            .attr("font-size", "12")
            .attr("stroke", "black")
            .attr("stroke-width", 1)
            .attr("fill", "white");
    });
};

const drawMapBorders = (data: RobotMapParsed, mapIndex = 0, svg: SvgSelection) => {
    const map = data.robotMap.maps[mapIndex];
    map.borders.map((border) => {
        drawGeometry(data.maps[mapIndex], svg, border.geometry, {
            fill: "#ffffffaa",
            stroke: "blue",
        });
    });
};

const drawMapDoors = (data: RobotMapParsed, mapIndex = 0, svg: SvgSelection) => {
    const map = data.robotMap.maps[mapIndex];
    map.doors.map((door) => {
        drawGeometry(data.maps[mapIndex], svg, door.geometry, {
            fill: "white",
            stroke: "red",
            strokeWidth: 2,
        });
    });
};

const drawPoses2d = (data: RobotMapParsed, mapIndex = 0, svg: SvgSelection) => {
    const map = data.robotMap.maps[mapIndex];
    map.poses2d.map((pose) => {
        drawPoint2d(svg, pose.coordinates.map((v: number) => myScale(v)) as [number, number], {
            fill: "red",
            stroke: "red",
            strokeWidth: 2,
        });
    });
};

const parseRobotMap2dPoints = (map: RobotMap) => {
    const points2d = map.points2d.map((robotPoint2d: RobotPoint2d) => ({
        [robotPoint2d.id]: robotPoint2d.coordinates,
    })).reduce((a: RobotPoints2dMap, b: RobotPoints2dMap) => ({ ...a, ...b }));
    return points2d;
};

const parseRobotMapFormat = (robotMap: RobotMapFormat) => {
    const data: RobotMapParsed = {
        maps: [],
        robotMap,
    };
    robotMap.maps.forEach((map: RobotMap, index: number) => {
        data.maps[index] = {
            mapIndex: index,
            points2d: parseRobotMap2dPoints(map),
        };
    });
    return data;
};

export const drawMap = (robotMap: RobotMapFormat, index = 0, selector: string) => {
    const mapParsed = parseRobotMapFormat(robotMap);
    const width = 800;
    const height = 600;
    setMapHeader("#map-header", mapParsed, index);
    const svg = d3.select(selector)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", "0,0,800,600")
        .attr("preserveAspectRation", true);
    drawMapRegions(mapParsed, index, svg);
    drawMapDoors(mapParsed, index, svg);
    drawMapBorders(mapParsed, index, svg);
    drawPoses2d(mapParsed, index, svg);
};
