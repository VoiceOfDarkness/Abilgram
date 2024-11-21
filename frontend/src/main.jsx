import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import SuperTokens from "supertokens-auth-react";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-auth-react/recipe/session";
import socket from "./api/socket";

import "./index.css";
import App from "./App.jsx";

SuperTokens.init({
  appInfo: {
    appName: "abilgram",
    apiDomain: `${import.meta.env.VITE_WEBSITE_DOMAIN}`,
    websiteDomain: `${import.meta.env.VITE_WEBSITE_URL}`,
    apiBasePath: "/auth",
    websiteBasePath: "/auth",
  },
  recipeList: [EmailPassword.init(), Session.init()],
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
