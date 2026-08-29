import "@testing-library/jest-dom";

if (typeof window !== "undefined" && typeof SVGElement !== "undefined") {
  const svgProto = SVGElement.prototype as unknown as SVGGraphicsElement;
  if (!svgProto.getBBox) {
    svgProto.getBBox = () => ({
      x: 0,
      y: 0,
      width: 100,
      height: 100,
      top: 0,
      right: 100,
      bottom: 100,
      left: 0,
      toJSON: () => "",
    });
  }
}
