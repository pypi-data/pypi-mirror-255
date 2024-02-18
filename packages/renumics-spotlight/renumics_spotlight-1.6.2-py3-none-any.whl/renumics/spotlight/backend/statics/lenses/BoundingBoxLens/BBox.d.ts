interface BBoxProps {
    x: number;
    y: number;
    width: number;
    height: number;
    color: string;
    label: string;
}
declare const BBox: ({ x, y, width, height, color, label }: BBoxProps) => JSX.Element;
export default BBox;
