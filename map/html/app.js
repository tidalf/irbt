import { drawMap, robotMapData } from "./js/robmap.js";

window.onload = () => {
    drawMap(robotMapData, 0, "#map");
};
