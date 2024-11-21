const getImageUrl = (avatarPath) => {
  if (!avatarPath) return "";
  if (avatarPath.startsWith("http")) return avatarPath;
  return `${import.meta.env.VITE_API_URL || ""}/media/${avatarPath}`;
};

export default getImageUrl;
