from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.core.models import RefreshToken
from app.core.enums import SecurityEventType
from app.core.utils.security import log_security_event
from app.core.utils.geoip import get_country_from_ip


async def detect_suspicious_login(
    db,
    request,
    user,
    ip_address,
    user_agent,
):
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .order_by(RefreshToken.created_at.desc())
    )

    sessions = result.scalars().all()

    known_ips = {s.ip_address for s in sessions if s.ip_address}
    known_agents = {s.user_agent for s in sessions if s.user_agent}

    
    


    current_country = get_country_from_ip(ip_address)

    print("IP:", ip_address)

    print("Country:", current_country)

    previous_country = None
    previous_time = None

    if sessions:
        last = sessions[0]

        previous_country = get_country_from_ip(last.ip_address)
        previous_time = last.created_at

    # New IP detection
    if known_ips and ip_address not in known_ips:
        await log_security_event(
            db,
            SecurityEventType.suspicious_login_ip,
            request,
            user_id=str(user.id),
        )

    # New device detection
    if known_agents and user_agent not in known_agents:
        await log_security_event(
            db,
            SecurityEventType.suspicious_login_device,
            request,
            user_id=str(user.id),
        )

    # New country detection
    if previous_country and current_country != previous_country:
        await log_security_event(
            db,
            SecurityEventType.suspicious_login_country,
            request,
            user_id=str(user.id),
        )

    # Impossible travel detection
    if previous_country and previous_time:
        time_diff = datetime.now(timezone.utc) - previous_time

        if current_country != previous_country and time_diff < timedelta(hours=2):
            await log_security_event(
                db,
                SecurityEventType.impossible_travel_login,
                request,
                user_id=str(user.id),
            )
