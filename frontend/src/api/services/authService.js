import { signUp } from "supertokens-web-js/recipe/emailpassword";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-web-js/recipe/session";
import apiClient from "../client";

export const authService = {
  registerWithSupertokens: async (email, password) => {
    const response = await signUp({
      formFields: [
        {
          id: "email",
          value: email,
        },
        {
          id: "password",
          value: password,
        },
      ],
    });
    return response;
  },

  getCurrentUserId: async () => {
    try {
      const response = await apiClient.get("/user_id");
      return response.data.user_id;
    } catch (error) {
      console.error("Error fetching user ID:", error);
      throw error;
    }
  },

  saveUserData: async (userData) => {
    const response = await apiClient.post("/user/", userData);
    return response.data;
  },

  register: async (username, email, password) => {
    const supertokensResponse = await authService.registerWithSupertokens(
      email,
      password
    );

    console.log(supertokensResponse);

    if (supertokensResponse.status === "OK") {
      await authService.saveUserData({
        username,
        email,
        supertokens_id: supertokensResponse.user.id,
      });
      return supertokensResponse;
    }

    throw new Error("Registration failed");
  },

  login: async (email, password) => {
    const response = await EmailPassword.signIn({
      formFields: [
        { id: "email", value: email },
        { id: "password", value: password },
      ],
    });

    if (response.status !== "OK") {
      throw new Error("Invalid credentials");
    }

    return response;
  },

  logout: async () => {
    await Session.signOut();
  },
};
