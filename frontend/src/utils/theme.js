import { createContext, useState, useMemo } from "react";
import { createTheme } from "@mui/material/styles";

// color design tokens export
export const tokens = (mode) => ({
  ...(mode === "dark"
    ? {
        color1: {
            100: "#d7e0d9",
            200: "#afc2b3",
            300: "#88a38d",
            400: "#608567",
            500: "#386641",
            600: "#2d5234",
            700: "#223d27",
            800: "#16291a",
            900: "#0b140d"
        },
        color2: {
            100: "#e1ebdc",
            200: "#c3d6b8",
            300: "#a6c295",
            400: "#88ad71",
            500: "#6a994e",
            600: "#557a3e",
            700: "#405c2f",
            800: "#2a3d1f",
            900: "#151f10"
        },
        color3: {
            100: "#edf4dd",
            200: "#dce9bc",
            300: "#cadf9a",
            400: "#b9d479",
            500: "#a7c957",
            600: "#86a146",
            700: "#647934",
            800: "#435023",
            900: "#212811"
        },
        color4: {
            100: "#fcfaf5",
            200: "#faf6ec",
            300: "#f7f1e2",
            400: "#f5edd9",
            500: "#f2e8cf",
            600: "#c2baa6",
            700: "#918b7c",
            800: "#615d53",
            900: "#302e29"
        },
        color5: {
            100: "#f2dadb",
            200: "#e4b5b6",
            300: "#d79192",
            400: "#c96c6d",
            500: "#bc4749",
            600: "#96393a",
            700: "#712b2c",
            800: "#4b1c1d",
            900: "#260e0f"
        },
        grey: {
            100: "#141414",
            200: "#292929",
            300: "#3d3d3d",
            400: "#525252",
            500: "#666666",
            600: "#858585",
            700: "#a3a3a3",
            800: "#c2c2c2",
            900: "#e0e0e0",
          },
          light_gray: {
            100: "#fcf8f8",
            200: "#faf0f1",
            300: "#f7e9e9",
            400: "#f5e1e2",
            500: "#f2dadb",
            600: "#c2aeaf",
            700: "#918383",
            800: "#615758",
            900: "#302c2c"
        },
        darkGrey: {
          100: "#cfd0d1",
          200: "#9fa1a3",
          300: "#707274",
          400: "#404346",
          500: "#101418",
          600: "#0d1013",
          700: "#0a0c0e",
          800: "#06080a",
          900: "#030405"
      },
          white: {
            100: "#ffffff",
            200: "#ffffff",
            300: "#ffffff",
            400: "#ffffff",
            500: "#ffffff",
            600: "#cccccc",
            700: "#999999",
            800: "#666666",
            900: "#333333"
        },
        
      }
    : {
      light_gray: {
        900: "#fcf8f8",
        800: "#faf0f1",
        700: "#f7e9e9",
        600: "#f5e1e2",
        500: "#f2dadb",
        400: "#c2aeaf",
        300: "#918383",
        200: "#615758",
        100: "#302c2c"
    },
    darkGrey: {
      900: "#cfd0d1",
      800: "#9fa1a3",
      700: "#707274",
      600: "#404346",
      500: "#101418",
      400: "#0d1013",
      300: "#0a0c0e",
      200: "#06080a",
      100: "#030405"
  },
        color1: {
            100: "#0b140d",
            200: "#16291a",
            300: "#223d27",
            400: "#2d5234",
            500: "#386641",
            600: "#608567",
            700: "#88a38d",
            800: "#afc2b3",
            900: "#d7e0d9"
        },
        color2: {
            100: "#151f10",
            200: "#2a3d1f",
            300: "#405c2f",
            400: "#557a3e",
            500: "#6a994e",
            600: "#88ad71",
            700: "#a6c295",
            800: "#c3d6b8",
            900: "#e1ebdc"
        },
        color3: {
            100: "#212811",
            200: "#435023",
            300: "#647934",
            400: "#86a146",
            500: "#a7c957",
            600: "#b9d479",
            700: "#cadf9a",
            800: "#dce9bc",
            900: "#edf4dd"
        },
        color4: {
            100: "#302e29",
            200: "#615d53",
            300: "#918b7c",
            400: "#c2baa6",
            500: "#f2e8cf",
            600: "#f5edd9",
            700: "#f7f1e2",
            800: "#faf6ec",
            900: "#fcfaf5"
        },
        color5: {
            100: "#260e0f",
            200: "#4b1c1d",
            300: "#712b2c",
            400: "#96393a",
            500: "#bc4749",
            600: "#c96c6d",
            700: "#d79192",
            800: "#e4b5b6",
            900: "#f2dadb"
        },
        grey: {
            100: "#e0e0e0",
            200: "#c2c2c2",
            300: "#a3a3a3",
            400: "#858585",
            500: "#666666",
            600: "#525252",
            700: "#3d3d3d",
            800: "#292929",
            900: "#141414"
        },
        white: {
          100: "#ffffff",
          200: "#ffffff",
          300: "#ffffff",
          400: "#ffffff",
          500: "#ffffff",
          600: "#cccccc",
          700: "#999999",
          800: "#666666",
          900: "#333333"
      },
      
    }    
  )})

// mui theme settings
export const themeSettings = (mode) => {
  const colors = tokens(mode);
  return {
    palette: {
      mode: mode,
      ...(mode === "light" // object spread operator
        ? {
            // palette values for dark mode
            primary: {
              main: colors.color1[500],
            },
            secondary: {
              main: colors.color2[500],
            },
            neutral: {
              dark: colors.grey[700],
              main: colors.grey[500],
              light: colors.grey[100],
            },
            background: {
              default: colors.darkGrey[500],
            },
          }
        : {
            
            primary: {
              main: colors.color1[100],
            },
            secondary: {
              main: colors.color2[500],
            },
            neutral: {
              dark: colors.grey[700],
              main: colors.grey[500],
              light: colors.grey[100],
            },
            background: {
              default: colors.white[100],
            },
          }),
    },
    typography: {
      fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
      fontSize: 12,
      h1: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 40,
      },
      h2: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 32,
      },
      h3: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 24,
      },
      h4: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 20,
      },
      h5: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 16,
      },
      h6: {
        fontFamily: ["Source Sans Pro", "sans-serif"].join(","),
        fontSize: 14,
      },
    },
  };
};

// context for color mode
export const ColorModeContext = createContext({
  toggleColorMode: () => {},
});

export const useMode = () => {
  const [mode, setMode] = useState("dark");

  const colorMode = useMemo(
    () => ({
      
      toggleColorMode: () =>{
      
        setMode((prev) => (prev === "light" ? "dark" : "light"))
        console.log(mode)
      },
        
    }),
    []
  );

  const theme = useMemo(() => createTheme(themeSettings(mode)), [mode]);
  return [theme, colorMode];
};