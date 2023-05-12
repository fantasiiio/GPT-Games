class QuadTree {
    constructor(bounds, maxLevel, level = 0) {
        this.bounds = bounds;
        this.maxLevel = maxLevel;
        this.level = level;
        this.trackGeometry = {
            lines: [],
            arcs: []
        }
        this.divided = false;
    }

    intertTrackGeometry(trackGeometry) {
        // Check for intersections with lines
        for (const line of trackGeometry.lines) {
            this.insertLine(line);
        }

        // Check for intersections with arcs
        for (const arc of trackGeometry.arcs) {
            this.insertArc(arc);
        }
    }

    insertLine(line) {
        if (!this.bounds.isLinePartWithinRectangle(line)) {
            return;
        }

        if (this.level === this.maxLevel) {
            this.trackGeometry.lines.push(line);
            return;
        }

        if (!this.divided) {
            this.subdivide();
        }

        this.northwest.insertLine(line)
        this.northeast.insertLine(line)
        this.southwest.insertLine(line)
        this.southeast.insertLine(line)
    }

    insertArc(arc) {
        if (!this.bounds.isArcPartWithinRectangle(arc)) {
            return;
        }

        if (this.level === this.maxLevel) {
            this.trackGeometry.arcs.push(arc);
            return;
        }

        if (!this.divided) {
            this.subdivide();
        }

        this.northwest.insertArc(arc)
        this.northeast.insertArc(arc)
        this.southwest.insertArc(arc)
        this.southeast.insertArc(arc)

        return false;
    }

    subdivide() {
        const x = this.bounds.x;
        const y = this.bounds.y;
        const w = this.bounds.width / 2;
        const h = this.bounds.height / 2;

        const nwBounds = new Rectangle(x, y, w, h, 0, false);
        const neBounds = new Rectangle(x + w, y, w, h, 0, false);
        const swBounds = new Rectangle(x, y + h, w, h, 0, false);
        const seBounds = new Rectangle(x + w, y + h, w, h, 0, false);

        const nextLevel = this.level + 1;

        this.northwest = new QuadTree(nwBounds, this.maxLevel, nextLevel);
        this.northeast = new QuadTree(neBounds, this.maxLevel, nextLevel);
        this.southwest = new QuadTree(swBounds, this.maxLevel, nextLevel);
        this.southeast = new QuadTree(seBounds, this.maxLevel, nextLevel);

        this.divided = true;

    }

    query(rectangle, found = {
        lines: [],
        arcs: []
    }) {
        if (!this.bounds.isRectanglePartWithinRectangle(rectangle)) {
            return found;
        }

        found.lines = [...found.lines, ...this.trackGeometry.lines];
        found.arcs = [...found.arcs, ...this.trackGeometry.arcs];

        if (this.divided) {
            this.northwest.query(rectangle, found);
            this.northeast.query(rectangle, found);
            this.southwest.query(rectangle, found);
            this.southeast.query(rectangle, found);
        }

        return found;
    }

}