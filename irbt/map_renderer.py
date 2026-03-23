"""
Render iRobot map data as a PNG image.

Takes the JSON output from vector_map() and produces a floor plan image
with colored rooms, walls, doors, and keepout zones.
"""

import logging

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

ROOM_COLORS = {
    'living_room': (168, 216, 234),
    'kitchen': (255, 211, 182),
    'bedroom': (213, 196, 247),
    'bathroom': (181, 234, 215),
    'foyer': (255, 238, 173),
    'custom': (232, 232, 232),
    'office': (200, 220, 240),
    'dining_room': (240, 220, 200),
    'laundry': (220, 220, 240),
    'hallway': (230, 230, 210),
}

DEFAULT_ROOM_COLOR = (210, 210, 210)
FLOOR_COLOR = (245, 240, 232)
WALL_COLOR = (80, 80, 80)
DOOR_COLOR = (230, 160, 50)
KEEPOUT_COLOR = (220, 80, 80, 100)
BACKGROUND_COLOR = (255, 255, 255)
COVERAGE_COLOR = (180, 230, 180)


def _build_point_lookup(points2d):
    """Build a dict mapping point ID (str) to (x, y) tuple."""
    return {str(p['id']): tuple(p['coordinates']) for p in points2d}


def _resolve_polygon_ids(id_rings, point_lookup):
    """Convert a list of ID rings to a list of coordinate rings.

    Each ring is a list of point ID strings. Returns a list of
    lists of (x, y) tuples. Missing IDs are skipped with a warning.
    """
    rings = []
    for ring in id_rings:
        coords = []
        for pid in ring:
            if str(pid) in point_lookup:
                coords.append(point_lookup[str(pid)])
            else:
                logger.warning('Point ID %s not found in points2d', pid)
        if coords:
            rings.append(coords)
    return rings


def _resolve_linestring_ids(ids, point_lookup):
    """Convert a list of point IDs to a list of (x, y) tuples."""
    coords = []
    for pid in ids:
        if str(pid) in point_lookup:
            coords.append(point_lookup[str(pid)])
        else:
            logger.warning('Point ID %s not found in points2d', pid)
    return coords


def _compute_transform(all_coords, width, margin=60):
    """Compute scale and offset to map metric coords to pixels.

    Returns (scale, offset_x, offset_y, img_width, img_height).
    """
    if not all_coords:
        raise ValueError('No coordinates to compute transform')

    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range == 0 or y_range == 0:
        raise ValueError('Map has zero extent')

    scale = (width - 2 * margin) / x_range
    img_height = int(y_range * scale + 2 * margin)

    return scale, x_min, y_min, width, img_height


def _transform_point(coord, scale, x_min, y_min, margin, img_height):
    """Convert a metric (x, y) to pixel (px, py), flipping Y."""
    px = (coord[0] - x_min) * scale + margin
    py = img_height - ((coord[1] - y_min) * scale + margin)
    return (int(px), int(py))


def _transform_coords(coords, scale, x_min, y_min, margin, img_height):
    """Transform a list of metric coords to pixel coords."""
    return [_transform_point(c, scale, x_min, y_min, margin, img_height)
            for c in coords]


def _polygon_centroid(points):
    """Compute the centroid of a polygon as (x, y)."""
    n = len(points)
    if n == 0:
        return (0, 0)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    return (int(cx), int(cy))


def _get_room_color(region_type):
    """Get fill color for a room type."""
    return ROOM_COLORS.get(region_type, DEFAULT_ROOM_COLOR)


def _get_font(size=14):
    """Try to load a TrueType font, fall back to default."""
    try:
        return ImageFont.truetype('Arial', size)
    except (IOError, OSError):
        try:
            return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',
                                      size)
        except (IOError, OSError):
            try:
                return ImageFont.truetype(
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
            except (IOError, OSError):
                return ImageFont.load_default()


def _collect_all_coords(map_entry, point_lookup):
    """Collect all coordinates from the map for bounding box computation."""
    all_coords = list(point_lookup.values())

    for layer in map_entry.get('layers', []):
        geom = layer.get('geometry', {})
        if 'coordinates' in geom:
            coords = geom['coordinates']
            if coords and isinstance(coords[0], list):
                if isinstance(coords[0][0], (int, float)):
                    all_coords.extend([tuple(c) for c in coords])

    return all_coords


def render_map(map_data, output_path='map.png', width=1600,
               show_coverage=False):
    """Render an iRobot map as a PNG image.

    Args:
        map_data: The full JSON dict from vector_map() or loaded
                  from examplemap.json.
        output_path: Path to save the PNG file.
        width: Target image width in pixels.
        show_coverage: Whether to show the coverage layer.
    """
    maps = map_data.get('maps', [])
    if not maps:
        raise ValueError('No maps found in map data')

    map_entry = maps[0]
    point_lookup = _build_point_lookup(map_entry.get('points2d', []))
    all_coords = _collect_all_coords(map_entry, point_lookup)

    if not all_coords:
        raise ValueError('No coordinates found in map data')

    scale, x_min, y_min, img_w, img_h = _compute_transform(
        all_coords, width)
    t_args = (scale, x_min, y_min, 60, img_h)

    img = Image.new('RGBA', (img_w, img_h), BACKGROUND_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # 1. Draw coverage layer
    if show_coverage:
        for layer in map_entry.get('layers', []):
            if layer.get('layer_type') == 'coverage':
                geom = layer.get('geometry', {})
                coords = geom.get('coordinates', [])
                point_size = max(2, int(0.105 * scale / 2))
                for coord in coords:
                    px, py = _transform_point(coord, *t_args)
                    draw.rectangle(
                        [px - point_size, py - point_size,
                         px + point_size, py + point_size],
                        fill=COVERAGE_COLOR + (255,))

    # 2. Draw borders
    for border in map_entry.get('borders', []):
        geom = border.get('geometry', {})
        ids = geom.get('ids', [])
        rings = _resolve_polygon_ids(ids, point_lookup)
        free_type = border.get('free_type', 'free')

        for ring in rings:
            pixel_ring = _transform_coords(ring, *t_args)
            if len(pixel_ring) >= 3:
                if free_type == 'free':
                    draw.polygon(pixel_ring, fill=FLOOR_COLOR + (255,),
                                 outline=WALL_COLOR + (255,), width=2)
                else:
                    draw.polygon(pixel_ring, fill=WALL_COLOR + (255,),
                                 outline=WALL_COLOR + (255,), width=2)

    # 3. Draw rooms as semi-transparent overlays
    room_overlay = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
    room_draw = ImageDraw.Draw(room_overlay)

    room_labels = []
    for region in map_entry.get('regions', []):
        geom = region.get('geometry', {})
        ids = geom.get('ids', [])
        region_type = region.get('region_type', 'custom')
        name = region.get('name', '')
        color = _get_room_color(region_type)

        rings = _resolve_polygon_ids(ids, point_lookup)
        if rings:
            outer_ring = rings[0]
            pixel_ring = _transform_coords(outer_ring, *t_args)
            if len(pixel_ring) >= 3:
                room_draw.polygon(pixel_ring,
                                  fill=color + (100,),
                                  outline=color, width=2)
                centroid = _polygon_centroid(pixel_ring)
                room_labels.append((name, centroid))

    img = Image.alpha_composite(img, room_overlay)
    draw = ImageDraw.Draw(img)

    # 4. Draw room labels with text shadow for readability
    font = _get_font(22)
    for name, (cx, cy) in room_labels:
        if not name:
            continue
        bbox = draw.textbbox((0, 0), name, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = cx - tw // 2
        ty = cy - th // 2

        # Draw white outline/shadow for contrast
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    draw.text((tx + dx, ty + dy), name,
                              fill=(255, 255, 255, 220), font=font)
        draw.text((tx, ty), name, fill=(60, 60, 60, 255), font=font)

    # 5. Draw doors
    for door in map_entry.get('doors', []):
        geom = door.get('geometry', {})
        ids = geom.get('ids', [])
        coords = _resolve_linestring_ids(ids, point_lookup)
        if len(coords) >= 2:
            pixel_coords = _transform_coords(coords, *t_args)
            draw.line(pixel_coords, fill=DOOR_COLOR + (255,), width=4)

    # 6. Draw keepout zones
    keepout_overlay = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
    keepout_draw = ImageDraw.Draw(keepout_overlay)
    for kz in map_entry.get('keepoutzones', []):
        geom = kz.get('geometry', {})
        ids = geom.get('ids', [])
        rings = _resolve_polygon_ids(ids, point_lookup)
        if rings:
            outer_ring = rings[0]
            pixel_ring = _transform_coords(outer_ring, *t_args)
            if len(pixel_ring) >= 3:
                keepout_draw.polygon(pixel_ring,
                                     fill=KEEPOUT_COLOR,
                                     outline=(220, 80, 80, 200), width=2)
    img = Image.alpha_composite(img, keepout_overlay)

    # 7. Draw map title
    header = map_entry.get('map_header', {})
    map_name = header.get('name', '')
    if map_name:
        draw = ImageDraw.Draw(img)
        title_font = _get_font(22)
        draw.text((15, 10), map_name, fill=(40, 40, 40, 255),
                  font=title_font)

    img.save(output_path, 'PNG')
    logger.info('Map saved to %s', output_path)
    return output_path
