def row_to_shipment(row):
    if row is None:
        return None

    return {
        "shipment_id": row[0],
        "order_id": row[1],
        "origin": row[2],
        "destination": row[3],
        "weight_kg": float(row[4]),
        "created_at": row[5].isoformat()
    }


def row_to_carrier(row):
    if row is None:
        return None

    return {
        "carrier_id": row[0],
        "name": row[1],
        "email": row[2],
        "phone": row[3],
        "is_active": bool(row[4])
    }


def row_to_status_update(row):
    if row is None:
        return None

    return {
        "update_id": row[0],
        "shipment_id": row[1],
        "carrier_id": row[2],
        "status": row[3],
        "location": row[4],
        "notes": row[5],
        "timestamp": row[6].isoformat()
    }
