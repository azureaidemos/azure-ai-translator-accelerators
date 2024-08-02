import { useState, useCallback } from "react";
import { ErrorNotification } from "../components/notifications/ErrorNotification";
import { SuccessNotification } from "../components/notifications/SuccessNotification";

const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback(
    (type, message = "") => {
      const id = Date.now();
      const newNotification = {
        id,
        message,
        NotificationComponent:
          type === "error" ? ErrorNotification : SuccessNotification,
      };
      setNotifications((prevNotifications) => [
        ...prevNotifications,
        newNotification,
      ]);

      setTimeout(() => {
        setNotifications((prevNotifications) =>
          prevNotifications.filter((notification) => notification.id !== id)
        );
      }, 5000);
    },
    [setNotifications]
  );

  return { notifications, addNotification };
};

export default useNotifications;
