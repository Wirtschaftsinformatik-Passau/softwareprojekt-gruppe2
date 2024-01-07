import { Box } from "@mui/material";


export const NoRowsOverlay = (message: string) => {
    return (
      <Box sx={{ padding: 10, textAlign: 'center' }}>
        {message}
      </Box>
    );
  };