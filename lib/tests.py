from termcolor import colored

def __check_credentials():
    pass


def __check_total_images(files_received, total_org_images):
    assert len(files_received) == total_org_images, print(colored("❌ \tMissing files", "red"))
    print(colored("✅ \tAll files are present in Nakala", "green"))

def __check_order_images(files_received, sorted_org_images):
    try:
        for file_received, file_org in zip(files_received, sorted_org_images):
            assert file_received == file_org, print(colored("❓\tOrder files are not the same. "
                                                        "Don't worry, this happens when you use method 'hard' or you have retried requests."
                                                        "You can always reorder them in Nakala frontend", "yellow"))
            print(colored("✅ \tfiles are in good order", "green"))
    except:
        pass


