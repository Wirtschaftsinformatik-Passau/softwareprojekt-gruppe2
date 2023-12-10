import { Box, useTheme } from "@mui/material";
import Header from "../../utility/Header";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { tokens } from "../../../utils/theme";

interface AccordionProps {
    title: string;
    text: string;
  }
  
interface FAQProps {
    items: AccordionProps[];
  }
  

const FAQ: React.FC <FAQProps> = ({items}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <Box m="20px">
      <Header title="FAQ" subtitle="Frequently Asked Questions Page" />
      {items && (items.map((item, index) => (
    <Accordion key={index} defaultExpanded sx={{
      backgroundColor: colors.color1[400],
    }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography color={colors.grey[300]} variant="h5">
          {item.title}
        </Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography>
          {item.text}
        </Typography>
      </AccordionDetails>
    </Accordion>)
        ))}
    </Box>
  );
};

export default FAQ;