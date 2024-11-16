const getImageUrl = (avatarPath) => {
  if (!avatarPath) return "";
  if (avatarPath.startsWith("http")) return avatarPath;
  return `http://localhost:8000/media/${avatarPath}`;
};

export default getImageUrl;
