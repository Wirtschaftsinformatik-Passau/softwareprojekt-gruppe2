import React from "react";
import { Box, useTheme } from "@mui/material";
import Header from "../../utility/Header";



const AdminUserEdit: React.FC = () => {
  const theme = useTheme();
  return (
    <Box m="20px">
      <Header title="AdminUserEdit" subtitle="AdminUserEdit Page" />
    </Box>
  );
};

export default AdminUserEdit;