import React, { useState, useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import ProfileDialog from "./Profile";
import debounce from "lodash.debounce";
import getImageUrl from "@/helpers/imageUrl";
import { searchService } from "@/api/services/searchService";
import { userService } from "@/api/services/userService";
import { authService } from "@/api/services/authService";
import socket from "@/api/socket";

function SearchIcon(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {...props}>
      <path
        fill="currentColor"
        d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 001.48-5.34c-.47-2.78-2.98-5-5.83-5.34a6.505 6.505 0 00-7.27 7.27c.34 2.85 2.56 5.36 5.34 5.83a6.5 6.5 0 005.34-1.48l.27.28v.79l4.25 4.25 1.25-1.25-4.25-4.25zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
      />
    </svg>
  );
}

function ListSearch({ searchQuery, setSearchQuery, onChatCreate }) {
  const [userProfile, setUserProfile] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);

  useEffect(() => {
    fetchInitialData();
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      const [profile, userId] = await Promise.all([
        userService.getProfile(),
        authService.getCurrentUserId(),
      ]);
      setUserProfile(profile);
      setCurrentUserId(userId);
    } catch (error) {
      console.error("Error fetching initial data:", error);
    }
  };

  const handleClickOutside = (event) => {
    if (searchRef.current && !searchRef.current.contains(event.target)) {
      setShowResults(false);
    }
  };

  const debouncedSearch = debounce(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const results = await searchService.searchUsers(query);
      const filteredResults = results.filter(
        (user) => user.id !== currentUserId
      );
      setSearchResults(filteredResults);
    } catch (err) {
      setError("Failed to search users");
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  }, 300);

  useEffect(() => {
    if (searchQuery) {
      debouncedSearch(searchQuery);
    } else {
      setSearchResults([]);
    }
    return () => debouncedSearch.cancel();
  }, [searchQuery]);

  const handleUserSelect = async (user) => {
    try {
      await searchService.createChat(user.id);

      const chatData = await searchService.createChat(user.id);
      socket.emit("chat", { user_id: user.id, chat: chatData });
      setShowResults(false);
      setSearchQuery("");
      onChatCreate();
    } catch (error) {
      console.error("Error handling user selection:", error);
    }
  };

  return (
    <div className="relative" ref={searchRef}>
      <div className="flex items-center gap-2 p-3 justify-between">
        <ProfileDialog onProfileUpdate={fetchInitialData} />
        <div className="flex-1 relative">
          <Input
            type="text"
            className="w-full pl-10 bg-gray-800 border-gray-600 text-white"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowResults(true);
            }}
            onFocus={() => setShowResults(true)}
          />
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <SearchIcon width={16} height={16} />
          </div>
        </div>
      </div>

      {showResults && searchQuery && (
        <div className="absolute z-50 left-0 right-0 mx-3 bg-gray-800 border border-gray-600 rounded-md shadow-lg mt-1">
          {isLoading && (
            <div className="text-center p-4 text-gray-400">Searching...</div>
          )}

          {error && <div className="text-center p-4 text-red-400">{error}</div>}

          {!isLoading && searchResults.length > 0 && (
            <ScrollArea className="max-h-64">
              {searchResults.map((user) => (
                <div
                  key={user.id || user.supertokens_id}
                  className="p-3 hover:bg-gray-700 flex items-center gap-3 cursor-pointer"
                  onClick={() => handleUserSelect(user)}
                >
                  <Avatar className="w-8 h-8">
                    <AvatarImage
                      src={getImageUrl(user.avatar_url)}
                      alt={user.username}
                    />
                    <AvatarFallback className="bg-cyan-950">
                      {user.username?.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium text-white">
                      {user.username}
                    </p>
                    {user.email && (
                      <p className="text-xs text-gray-400">{user.email}</p>
                    )}
                  </div>
                </div>
              ))}
            </ScrollArea>
          )}

          {!isLoading && searchResults.length === 0 && (
            <div className="text-center p-4 text-gray-400">No users found</div>
          )}
        </div>
      )}
    </div>
  );
}

export default ListSearch;
