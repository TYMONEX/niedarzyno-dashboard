const map = L.map("map", { zoomControl: true, minZoom: 12 });

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

const pointsLayer = L.layerGroup().addTo(map);
const zonesLayer = L.layerGroup().addTo(map);
const allBounds = L.latLngBounds();

function escapeHtml(value) {
    return String(value || "").replace(/[&<>'"]/g, ch => ({
        "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"
    }[ch]));
}

function popupHtml(properties) {
    const description = properties.description
        ? `<div class="popup-description">${escapeHtml(properties.description)}</div>`
        : "";
    return `<div class="popup-label">${properties.kind === "punkt" ? "PUNKT" : "OBSZAR"}</div>
            <div class="popup-title">${escapeHtml(properties.name)}</div>${description}`;
}

function markerIcon(color) {
    return L.divIcon({
        className: "marker-wrapper",
        html: `<div class="custom-marker" style="background:${color}"></div>`,
        iconSize: [28, 34],
        iconAnchor: [14, 32],
        popupAnchor: [0, -30]
    });
}

fetch("/static/niedarzyno.geojson")
    .then(response => {
        if (!response.ok) throw new Error("Nie udało się załadować danych mapy.");
        return response.json();
    })
    .then(data => {
        data.features.forEach(feature => {
            const p = feature.properties;
            const color = p.color || "#7657ff";
            let layer;

            if (feature.geometry.type === "Point") {
                const [lon, lat] = feature.geometry.coordinates;
                layer = L.marker([lat, lon], { icon: markerIcon(color) });
                layer.bindPopup(popupHtml(p), { maxWidth: 330 });
                layer.addTo(pointsLayer);
                allBounds.extend([lat, lon]);
            } else if (feature.geometry.type === "Polygon") {
                const latLngs = feature.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
                layer = L.polygon(latLngs, {
                    color,
                    weight: 2,
                    opacity: .95,
                    fillColor: color,
                    fillOpacity: .24
                });
                layer.bindPopup(popupHtml(p), { maxWidth: 330 });
                layer.on("mouseover", () => layer.setStyle({ fillOpacity: .38, weight: 3 }));
                layer.on("mouseout", () => layer.setStyle({ fillOpacity: .24, weight: 2 }));
                layer.addTo(zonesLayer);
                latLngs.forEach(ll => allBounds.extend(ll));
            }
        });

        if (allBounds.isValid()) map.fitBounds(allBounds.pad(.08));
        else map.setView([54.219, 17.428], 14);
    })
    .catch(error => {
        console.error(error);
        map.setView([54.219, 17.428], 14);
    });

document.querySelectorAll(".filter").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".filter").forEach(b => b.classList.remove("active"));
        button.classList.add("active");
        const filter = button.dataset.filter;

        if (filter === "all" || filter === "points") {
            if (!map.hasLayer(pointsLayer)) pointsLayer.addTo(map);
        } else map.removeLayer(pointsLayer);

        if (filter === "all" || filter === "zones") {
            if (!map.hasLayer(zonesLayer)) zonesLayer.addTo(map);
        } else map.removeLayer(zonesLayer);
    });
});

document.getElementById("fit-map").addEventListener("click", () => {
    if (allBounds.isValid()) map.fitBounds(allBounds.pad(.08));
});
