import * as fs from "fs";
import { promisify } from "util";

const readFile = promisify(fs.readFile);

export const readJson = async<T>(path: string): Promise<T | Error> => {
    const content = await readFile(path);
    let parsed;
    try {
        parsed = JSON.parse(content.toString());
    } catch (e) {
        return e;
    }
    return parsed as T;
};
