export const formatMessageTime = (dateString) => {
    if (!dateString) return "";

    const messageDate = new Date(dateString);
    const now = new Date();
    const diff = now - messageDate;

    // Adjust the messageDate to UTC+4
    messageDate.setHours(messageDate.getHours() + 4);

    if (diff < 24 * 60 * 60 * 1000) {
        return messageDate.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    if (diff < 7 * 24 * 60 * 60 * 1000) {
        return messageDate.toLocaleDateString([], { weekday: "short" });
    }

    return messageDate.toLocaleDateString([], {
        month: "short",
        day: "numeric",
    });
};
