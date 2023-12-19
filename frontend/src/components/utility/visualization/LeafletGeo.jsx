import { MapContainer, TileLayer, Marker, Popup} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import pin from "../../../assets/pin_icon.png"

const greenNeedleIcon = new L.Icon({
    iconUrl: pin,
    iconRetinaUrl: pin,
    popupAnchor:  [-0, -0],
    iconSize: [20,22],     
});
const centerPosition = [48.57387642605738, 13.463158783687527]; 
const initialZoom = 14;



  const MapWithCoordinates = ({locations = locations}) => {
    console.log(locations)

    return (
      <MapContainer center={centerPosition}  initialZoom={initialZoom} zoom={initialZoom} scrollWheelZoom={true} style={{ height: '400px', width: '100%' }}>
        <TileLayer
        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
      />
        {locations.map(location => (
          <Marker key={location.id} position={location.position} icon={greenNeedleIcon}>
            <Popup>Haushalt ID: {location.name}</Popup>
          </Marker>
        ))}
      </MapContainer>
    );
  };

export default MapWithCoordinates;