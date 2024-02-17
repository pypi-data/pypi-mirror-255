import { IChartForExport } from "@kanaries/graphic-walker/dist/interfaces";
export declare function usePythonCode(props: {
    sourceCode: string;
    visSpec: IChartForExport[];
    version: string;
}): {
    pyCode: string;
};
