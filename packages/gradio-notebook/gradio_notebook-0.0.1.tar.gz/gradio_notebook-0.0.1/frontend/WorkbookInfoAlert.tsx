import { Alert, Anchor, Text, createStyles } from "@mantine/core";
import { IconClearAll } from "@tabler/icons-react";
import { memo, useState } from "react";

// Hacky, but we need to explicitly set mantine style here since gradio overrides
// with `.gradio-container-id a` specificity for anchor elements.
// See mantine-color-anchor definition in
// https://github.com/mantinedev/mantine/blob/d1f047bd523f8f36ab9edf3aff5f6c2948736c5a/packages/%40mantine/core/src/core/MantineProvider/global.css#L353
// TODO: Remove once overall style problem is fixed
const useStyles = createStyles((theme) => ({
  link: {
    color: `${
      theme.colorScheme === "dark" ? theme.colors.blue[4] : theme.primaryColor
    } !important`,
  },
}));

export default memo(function WorkbookInfoAlert() {
  const { classes } = useStyles();
  const [isAlertVisible, setIsAlertVisible] = useState<boolean>(true);

  return (
    <Alert
      color="blue"
      hidden={!isAlertVisible}
      mb="8px"
      onClose={() => setIsAlertVisible(false)}
      withCloseButton
    >
      <Text>
        This is a{" "}
        <Anchor
          href="https://aiconfig.lastmileai.dev/docs/gradio-workbook"
          target="_blank"
          className={classes.link}
        >
          Gradio Workbook
        </Anchor>{" "}
        - playground for Hugging Face models! The workbook is made up of cells:
      </Text>
      <Text>
        1. <strong>Select a model</strong>: Add a cell with '+'. Click on the
        Cell Settings button (
        <IconClearAll
          size="18"
          style={{ display: "inline", paddingBottom: 2 }}
        />
        ).
      </Text>
      <Text>
        2. <strong>Set default view for space</strong>: Click 'Download' and
        upload the downloaded file to your space repo as `my_app.aiconfig.json`.
      </Text>
      <Text>
        3. <strong>Share your workbook state</strong>: Click 'Share Workbook' to
        generate a link to the read-only copy of your workbook state.
      </Text>
    </Alert>
  );
});
