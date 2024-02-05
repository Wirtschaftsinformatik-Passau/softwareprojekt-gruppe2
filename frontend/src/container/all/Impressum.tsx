import React from 'react';
import { Container, Typography, List, ListItem, ListItemText, Divider, Box, Button } from '@mui/material';
import Link from '@mui/material/Link';
import { useNavigate } from 'react-router-dom';
import {useTheme } from "@mui/material"
import Header from '../../components/utility/Header';


import { tokens } from '../../utils/theme';

const ImpressumPage = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const navigate = useNavigate();
    return (
      <Container component="main" maxWidth="md" sx={{ mt: 4, mb: 4 , color:colors.color1[500]}}>
        <Button  sx={{background: colors.color1[400], color: theme.palette.background.default}} 
        variant="contained" onClick={() => navigate(-1)}>
                                Zurück
                            </Button>
        <Header title="Impressum" subtitle="Alle Informationen zu unserem Unternehmen" />
        <Typography variant="h4" gutterBottom sx={{ mb: 2 }}>
          Impressum
        </Typography>
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Kontakt:
          </Typography>
          <List>
            <ListItem disablePadding>
              <ListItemText primary="E-Mail: musternetzbetreiber@e-mail.com" />
            </ListItem>
            <ListItem disablePadding>
              <ListItemText primary="Telefon: 0871-95 38 68 02" />
            </ListItem>
            <ListItem disablePadding>
              <ListItemText primary="Montag bis Freitag 07:00-20:00 Uhr" />
            </ListItem>
          </List>
        </Box>
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Name und Anschrift:
          </Typography>
          <Typography>
            Musternetzbetreiber GmbH<br />
            Hauptstraße 1<br />
            12345 Musterstadt<br />
            Deutschland
          </Typography>
        </Box>
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Geschäftsführung:
          </Typography>
          <Typography>
            Dr. Erika Musterfrau (Vorsitzende der Geschäftsführung), Dr. Max Mustermann, Henriette Musterfrau, Tobias Mustermann
          </Typography>
        </Box>
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Vorsitzender des Aufsichtsrats:
          </Typography>
          <Typography>
            Gerhard Mustermann
          </Typography>
        </Box>
  
        <Box sx={{ mb: 4 }}>
          <Typography>
            Sitz: Hauptstraße 1, 12345 Musterstadt, Amtsgericht Musterstadt, HRB 209319<br />
            Steuernummer: 9142/494/37372, Umsatzsteuer-ID: DE258833448,<br />
            Gläubiger-ID: DE41GLOBAL00002122393
          </Typography>
        </Box>
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Verantwortliche gemäß §18 Abs. 2 MStV
          </Typography>
          <Typography>
            Julia Musterfrau<br />
            Hauptstraße 1<br />
            12345 Musterstadt
          </Typography>
        </Box>
  
        <Divider sx={{ my: 4 }} />
  
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Cookie Policy
          </Typography>
          <Typography paragraph>
            Einwilligung in die Datenverarbeitung
          </Typography>
          <Typography paragraph>
          Wir setzen auf unserer Website Cookies und Tracking-Technologien ein. Der Einsatz von sogenannten technisch notwendigen Cookies ist für die Nutzung unserer Website notwendig. Zusätzlich können Sie uns, mit einem Klick auf die Schaltfläche „Akzeptieren“ für die folgenden Verarbeitungen Ihre Einwilligung geben:  
            <List sx={{ listStyleType: 'disc' }}>
                <ListItem sx={{ display: 'list-item' }}>
                <ListItemText>
                Speicherung von Informationen auf Ihrem Endgerät und dem Zugriff auf Informationen in Ihrem Endgerät.  
                </ListItemText>
                </ListItem>
                <ListItem sx={{ display: 'list-item' }}>
                <ListItemText>
                Analyse- und Marketingzwecken sowie für das Ausspielen von personalisierten Inhalten sowie Anwendungen des maschinellen Lernens.  
                </ListItemText>
                </ListItem>
                <ListItem sx={{ display: 'list-item' }}>
                <ListItemText>
                Verarbeitung Ihrer personenbezogenen Daten für die geräteübergreifende Erstellung und Verarbeitung von individuellen Nutzungsprofilen auf dieser Webseite und durch unsere Partner.   
                </ListItemText>
                </ListItem>
                <ListItem sx={{ display: 'list-item' }}>
                <ListItemText>
                Übermittlung Ihrer Daten in Ländern außerhalb der Europäischen Union (EU), namentlich in die USA sowie in andere Drittländer. In diesen Drittländern ist das Datenschutzniveau nicht mit dem Datenschutzniveau in der Europäischen Union vergleichbar. Hierbei besteht das Risiko, dass Ihre Daten durch Behörden, zu Überwachungs- sowie Kontrollzwecken, verarbeitet werden können. Diese Zielländer werden in der jeweiligen Beschreibung der Dienste in den individuellen Einstellungen und in unserer Datenschutzerklärung angegeben.
                </ListItemText>
                </ListItem >
                Weitere Informationen, auch zur Datenverarbeitung durch Drittanbieter und zum jederzeit möglichen Widerruf Ihrer Einwilligung, finden Sie unter dem Punkt „Cookie Einstellungen“ sowie in unseren Datenschutzhinweisen. Die jeweiligen Verarbeitungen, die Sie gestatten wollen, können Sie in den „Cookie Einstellungen“ auswählen und mit „Speichern“ bestätigen.  
            </List>
          </Typography>
        </Box>
  
        <Divider sx={{ my: 4 }} />
  
        <Box>
          <Typography variant="h4" gutterBottom>
            Datenschutzrichtlinien
          </Typography>
          <Typography variant="h4">Webseitenfunktionen</Typography>
          <Typography variant="h5">1. Abruf der Webseite</Typography>
          <Typography paragraph>
            Der Abruf dieser Webseite durch Sie erfordert die Verarbeitung Ihrer personenbezogenen Daten, etwa der IP-Adresse. Eine weitergehende Verarbeitung personenbezogener Daten bei der Verwendung besonderer Dienste oder Cookies wird gesondert dargestellt. 
          </Typography>
          <Typography paragraph>
          Bei Ihrem Abruf dieser Webseite verarbeiten wir Ihre personenbezogenen Daten, um Ihnen diese Webseite bereitzustellen sowie um deren Betrieb und technische Sicherheit zu gewährleisten.   
          </Typography>
          <Typography paragraph>
          Ihre IP-Adresse, Browserdaten (z.B. Referrer-ID oder Weiterleitungen, Bildschirmauflösung, Betriebssystem, Browser und Browserversion, installierte Plug-Ins und Erweiterungen sowie Schriftarten). 
          </Typography>
          <Typography paragraph>
          Die Verarbeitung Ihrer personenbezogenen Daten bei Ihrem Abruf dieser Webseite erfolgt aufgrund unseres berechtigten Interesses (Art. 6 Abs. 1 lit. f DSGVO). 
Wir haben unser Interesse an der Bereitstellung sowie am Betrieb und der Sicherung dieser Webseite gegen Ihr Interesse an der Vertraulichkeit Ihrer personenbezogenen Daten miteinander abgewogen, wobei unser Interesse überwiegt. Ohne die Verarbeitung der personenbezogenen Daten ist eine Bereitstellung der Webseite technisch nicht möglich. Dies gilt ebenso für deren Betreib und Sicherung. Dabei dient die Sicherung der Webseite auch Ihren Interessen.           
        </Typography>
          <Typography paragraph>
          Wir legen Ihre personenbezogenen Daten nicht gegenüber Empfängern offen. 
                    </Typography>
                    <Typography paragraph>
                    Wir speichern Ihre Daten so lange, wie dies für Bereitstellung den oben bezeichneten Diensten Ihnen gegenüber erforderlich ist. 
                    </Typography>
                    <Typography paragraph>
                    Sie sind zu einer Bekanntgabe personenbezogener Daten nicht verpflichtet. Ohne Ihre personenbezogenen Daten ist der Abruf dieser Webseite für Sie aber nicht möglich. 
                    </Typography>
                    <Typography variant="h5">2. Technisch notwendige Cookies</Typography>
<Typography paragraph>
  Im Zusammenhang mit der Verwendung technisch notwendiger Cookies verarbeiten wir Ihre personenbezogenen Daten, um Ihnen bestimmte Funktionen dieser Webseite bereitzustellen.
</Typography>
<Typography paragraph>
  Bei dem Abruf dieser Webseite durch Sie können Ihre personenbezogenen Daten im Zusammenhang mit der Verwendung von sog. „Cookies“ verarbeitet werden. Cookies sind Textdateien, die auf Ihrem Endgerät gespeichert werden und für bestimmte Funktionen dieser Webseite erforderlich sind. Sie können Ihre Browser-Einstellung entsprechend Ihren Wünschen konfigurieren und z.B. die Annahme von Third-Party-Cookies oder allen Cookies ablehnen. Wir weisen Sie darauf hin, dass Sie eventuell nicht alle Funktionen dieser Webseite nutzen können. Dabei beziehen sich die nachfolgenden Informationen auf Cookies, die keinen Bezug zu einem über unsere Webseite verfügbaren Dienst haben, sondern ausschließlich der Bereitstellung der Webseite selbst dienen („technisch notwendige Cookies“).
</Typography>
<Typography paragraph>
  Google Tag Manager: Aggregierte Daten über die Tag-Auslösung Consent Management Plattform Usercentrics: Opt-in- und Opt-out-Daten, Referrer URL, User Agent, Benutzereinstellungen, Consent ID, Zeitpunkt und Art der Einwilligung, Template Version, Banner-Sprache.
</Typography>
<Typography paragraph>
  Die Verarbeitung Ihrer personenbezogenen Daten im Zusammenhang mit der Verwendung technisch notwendiger Cookies auf dieser Webseite erfolgt aufgrund unseres berechtigten Interesses (Art. 6 Abs. 1 lit. f DSGVO). Wir haben unser Interesse an der Bereitstellung der von Cookies abhängigen Funktionen dieser Webseite gegen Ihr Interesse an der Vertraulichkeit Ihrer personenbezogenen Daten miteinander abgewogen, wobei unser Interesse überwiegt. Ohne die Verarbeitung der personenbezogenen Daten ist eine Bereitstellung der Funktionen technisch nicht möglich. Gleichzeitig steht Ihnen die oben dargestellte Möglichkeit offen, die Verarbeitung Ihrer personenbezogenen Daten im Zusammenhang mit Cookies zu unterbinden.
</Typography>
<Typography paragraph>
  Wir legen Ihre personenbezogenen Daten nicht gegenüber Empfängern offen.
</Typography>
<Typography paragraph>
  Wir speichern Ihre personenbezogenen Daten so lange, wie dies für die Verwendung des jeweiligen Cookies erforderlich ist.
</Typography>
<Typography paragraph>
  Sie sind zu einer Bekanntgabe personenbezogener Daten nicht verpflichtet. Ohne Ihre personenbezogenen Daten stehen Ihnen eventuell nicht alle Funktionen dieser Webseite zur Verfügung.
</Typography>
<Typography variant="h5">3. Local Storage</Typography>
<Typography paragraph>
  Wenn Sie eingewilligt haben, speichern wir von Ihnen auf unserer Webseite eingegebenen personenbezogenen Daten im sogenannten Local Storage in Ihrem Browser.
</Typography>
<Typography paragraph>
  Im Zusammenhang mit der Verwendung des Local Storage verarbeiten wir Ihre personenbezogenen Daten, um bestimmte Funktionen dieser Webseite zu gestalten. Das bedeutet, dass wir von Ihnen auf unserer Webseite eingegebene Informationen im Local Storage über Ihren jeweiligen Besuch unserer Webseite hinaus speichern. Auf diese Weise müssen Sie besagte Informationen bei künftigen Besuchen unserer Webseite nicht erneut eingeben, sondern bekommen diese direkt als Eingabevorschlag bereitgestellt.
</Typography>
<Typography paragraph>
  Kategorien personenbezogener Daten: Eingabeinformationen in Formularen sowie Daten aus Tracking-Tools, nicht jedoch Einwilligungen, Bankverbindungen oder Vertragskontonummern.
</Typography>
<Typography paragraph>
  Die Verarbeitung Ihrer personenbezogenen Daten im Zusammenhang mit der Verwendung des Local Storage auf dieser Webseite erfolgt aufgrund berechtigten Interesses (Art. 6 Abs. 1 lit. f DSGVO). 
</Typography>
<Typography paragraph>
  Wir legen Ihre personenbezogenen Daten nicht gegenüber Empfängern offen.
</Typography>
<Typography paragraph>
  Wir speichern Ihre personenbezogenen Daten so lange, wie dies für die Verwendung der jeweiligen, vom Local Storage abhängigen Funktion der Webseite erforderlich ist.
</Typography>
<Typography paragraph>
  Sie sind zu einer Bekanntgabe personenbezogener Daten nicht verpflichtet. Sie können Ihre Browser-Einstellung entsprechend Ihren Wünschen konfigurieren und z.B. die Verwendung des Local Storage zu deaktivieren. Ohne Ihre personenbezogenen Daten stehen Ihnen eventuell nicht alle Funktionen dieser Webseite zur Verfügung.
</Typography>
                    
        </Box>
      </Container>
    );
  };
  
  export default ImpressumPage;