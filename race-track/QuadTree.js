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

        if (this.level === this.maxLevel || this.bounds.width <= 500) {
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

        if (this.level === this.maxLevel || this.bounds.width <= 500) {
            this.trackGeometry.arcs.push(arc);
            return;
        } else {
            this.bounds.isArcPartWithinRectangle(arc);
            this.level = this.level;
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

    queryFromRectangle(rectangle, found = {
        lines: [],
        arcs: [],
        count: 0
    }) {
        if (!this.bounds.isRectanglePartWithinRectangle(rectangle)) {
            return found;
        }

        if (this.divided) {
            this.northwest.queryFromRectangle(rectangle, found);
            this.northeast.queryFromRectangle(rectangle, found);
            this.southwest.queryFromRectangle(rectangle, found);
            this.southeast.queryFromRectangle(rectangle, found);
        } else {
            found.lines = [...found.lines, ...this.trackGeometry.lines];
            found.arcs = [...found.arcs, ...this.trackGeometry.arcs];
            found.count++;
        }

        return found;
    }

    queryFromLine(line, found = {
        lines: [],
        arcs: []
    }) {
        if (!this.bounds.isLinePartWithinRectangle(line)) {
            return found;
        }

        if (this.divided) {
            this.northwest.queryFromLine(line, found);
            this.northeast.queryFromLine(line, found);
            this.southwest.queryFromLine(line, found);
            this.southeast.queryFromLine(line, found);
        } else {
            found.lines = [...found.lines, ...this.trackGeometry.lines];
            found.arcs = [...found.arcs, ...this.trackGeometry.arcs];            
        }

        return found;
    }

    queryFromPoint(point, found = {
        lines: [],
        arcs: []
    }) {
        if (!this.bounds.contains(point)) {
            return found;
        }

        found.lines = [...found.lines, ...this.trackGeometry.lines];
        found.arcs = [...found.arcs, ...this.trackGeometry.arcs];

        if (this.divided) {
            this.northwest.queryFromPoint(point, found);
            this.northeast.queryFromPoint(point, found);
            this.southwest.queryFromPoint(point, found);
            this.southeast.queryFromPoint(point, found);
        }

        return found;
    }

    drawFromRectangle(rectangle, ctx) {
        if (!this.bounds.isRectanglePartWithinRectangle(rectangle)) {
            return;
        }
        // Recursively draw child nodes
        if (this.divided) {
            this.northwest.drawFromRectangle(rectangle, ctx);
            this.northeast.drawFromRectangle(rectangle, ctx);
            this.southwest.drawFromRectangle(rectangle, ctx);
            this.southeast.drawFromRectangle(rectangle, ctx);
        } else {
            // Draw the current node bounds
            ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
            ctx.lineWidth = 2;
            ctx.strokeRect(this.bounds.x, this.bounds.y, this.bounds.width, this.bounds.height);
        }
    }

    drawFromLine(line, ctx) {
        if (!this.bounds.isLinePartWithinRectangle(line)) {
            return;
        }
        // Recursively draw child nodes
        if (this.divided) {
            this.northwest.drawFromLine(line, ctx);
            this.northeast.drawFromLine(line, ctx);
            this.southwest.drawFromLine(line, ctx);
            this.southeast.drawFromLine(line, ctx);
        } else {
            // Draw the current node bounds
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.lineWidth = 2;
            ctx.fillRect(this.bounds.x, this.bounds.y, this.bounds.width, this.bounds.height);
        }
    }

}