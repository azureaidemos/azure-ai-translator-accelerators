import { FaceFrownIcon } from "@heroicons/react/24/outline";
import { BaseNotification } from "./BaseNotification";

export const ErrorNotification = ({message="Something went wrong while uploading! Try again later or contact support!", ...props}) => {
  return (
    <BaseNotification
      {...props}
      Icon={<FaceFrownIcon />}
      title="File upload failed!"
      textColor="text-red-500"
      message={message}
    />
  );
};
