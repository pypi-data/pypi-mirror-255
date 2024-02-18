import { IAppProps } from './interfaces';
import type { IPreviewProps, IChartPreviewProps } from './components/preview';
declare function GWalker(props: IAppProps, id: string): void;
declare function PreviewApp(props: IPreviewProps, id: string): void;
declare function ChartPreviewApp(props: IChartPreviewProps, id: string): void;
declare const _default: {
    GWalker: typeof GWalker;
    PreviewApp: typeof PreviewApp;
    ChartPreviewApp: typeof ChartPreviewApp;
};
export default _default;
