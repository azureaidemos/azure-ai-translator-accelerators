import { FaceSmileIcon } from "@heroicons/react/24/outline";
import { BaseNotification } from "./BaseNotification";

export const SuccessNotification = ({message, ...props}) => {
  return (
    <BaseNotification
      {...props}
      Icon={<FaceSmileIcon />}
      title="File uploaded successfully!"
      textColor="text-emerald-500"
      message={message}
    />
  );
};
