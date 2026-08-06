import click

# Apple names each data type the same way in a privacy manifest and in the App Privacy questionnaire,
# so a manifest entry can be turned into the exact wording seen in App Store Connect. Only the prefix
# and the capitalisation differ, but guessing the label from the constant produces wrong wording for
# several of them, so the table is written out.
DATA_TYPE_LABELS = {
    "NSPrivacyCollectedDataTypeName": ("Contact Info", "Name"),
    "NSPrivacyCollectedDataTypeEmailAddress": ("Contact Info", "Email Address"),
    "NSPrivacyCollectedDataTypePhoneNumber": ("Contact Info", "Phone Number"),
    "NSPrivacyCollectedDataTypePhysicalAddress": ("Contact Info", "Physical Address"),
    "NSPrivacyCollectedDataTypeOtherUserContactInfo": ("Contact Info", "Other Contact Info"),
    "NSPrivacyCollectedDataTypeHealth": ("Health & Fitness", "Health"),
    "NSPrivacyCollectedDataTypeFitness": ("Health & Fitness", "Fitness"),
    "NSPrivacyCollectedDataTypePaymentInfo": ("Financial Info", "Payment Info"),
    "NSPrivacyCollectedDataTypeCreditInfo": ("Financial Info", "Credit Info"),
    "NSPrivacyCollectedDataTypeOtherFinancialInfo": ("Financial Info", "Other Financial Info"),
    "NSPrivacyCollectedDataTypePreciseLocation": ("Location", "Precise Location"),
    "NSPrivacyCollectedDataTypeCoarseLocation": ("Location", "Coarse Location"),
    "NSPrivacyCollectedDataTypeSensitiveInfo": ("Sensitive Info", "Sensitive Info"),
    "NSPrivacyCollectedDataTypeContacts": ("Contacts", "Contacts"),
    "NSPrivacyCollectedDataTypeEmails": ("User Content", "Emails or Text Messages"),
    "NSPrivacyCollectedDataTypePhotosorVideos": ("User Content", "Photos or Videos"),
    "NSPrivacyCollectedDataTypeAudioData": ("User Content", "Audio Data"),
    "NSPrivacyCollectedDataTypeGameplayContent": ("User Content", "Gameplay Content"),
    "NSPrivacyCollectedDataTypeCustomerSupport": ("User Content", "Customer Support"),
    "NSPrivacyCollectedDataTypeOtherUserContent": ("User Content", "Other User Content"),
    "NSPrivacyCollectedDataTypeBrowsingHistory": ("Browsing History", "Browsing History"),
    "NSPrivacyCollectedDataTypeSearchHistory": ("Search History", "Search History"),
    "NSPrivacyCollectedDataTypeUserID": ("Identifiers", "User ID"),
    "NSPrivacyCollectedDataTypeDeviceID": ("Identifiers", "Device ID"),
    "NSPrivacyCollectedDataTypePurchaseHistory": ("Purchases", "Purchase History"),
    "NSPrivacyCollectedDataTypeProductInteraction": ("Usage Data", "Product Interaction"),
    "NSPrivacyCollectedDataTypeAdvertisingData": ("Usage Data", "Advertising Data"),
    "NSPrivacyCollectedDataTypeOtherUsageData": ("Usage Data", "Other Usage Data"),
    "NSPrivacyCollectedDataTypeCrashData": ("Diagnostics", "Crash Data"),
    "NSPrivacyCollectedDataTypePerformanceData": ("Diagnostics", "Performance Data"),
    "NSPrivacyCollectedDataTypeOtherDiagnosticData": ("Diagnostics", "Other Diagnostic Data"),
    "NSPrivacyCollectedDataTypeEnvironmentScanning": ("Surroundings", "Environment Scanning"),
    "NSPrivacyCollectedDataTypeHands": ("Body", "Hands"),
    "NSPrivacyCollectedDataTypeHead": ("Body", "Head"),
    "NSPrivacyCollectedDataTypeOtherDataTypes": ("Other Data", "Other Data Types"),
}

PURPOSE_LABELS = {
    "NSPrivacyCollectedDataTypePurposeThirdPartyAdvertising": "Third-Party Advertising",
    "NSPrivacyCollectedDataTypePurposeDeveloperAdvertising": "Developer's Advertising or Marketing",
    "NSPrivacyCollectedDataTypePurposeAnalytics": "Analytics",
    "NSPrivacyCollectedDataTypePurposeProductPersonalization": "Product Personalization",
    "NSPrivacyCollectedDataTypePurposeAppFunctionality": "App Functionality",
    "NSPrivacyCollectedDataTypePurposeOther": "Other Purposes",
}


@click.group()
def privacy():
    """ Work out what to answer in Apple's App Privacy questionnaire.

    \f
    Apple requires every app to declare what data it collects before it can be submitted, and refuses to
    let that declaration be filled in by API — it has to be done on the App Store Connect website. What
    stops most people is not the clicking, it is knowing what to answer.

    Since May 2024 Apple requires every third-party library to ship a :code:`PrivacyInfo.xcprivacy` file
    declaring what it collects. Those files are machine readable, so most of the answer is already sitting
    in the project.

    Usage:
    """


@privacy.command()
@click.option('--directory', type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
              help="The Flutter project to scan. Defaults to the current directory.")
def scan(directory):
    """ Read the privacy manifests in the project and report what they declare.

    \f
    The report is meant to be read side by side with the App Privacy questionnaire: every data type is
    given under the exact heading Apple uses, together with whether it is linked to the user and whether
    it is used for tracking, which are the two questions Apple asks about each one.

    Dependencies that ship no manifest are listed separately. Their silence is not a promise: it means
    nothing can be concluded about them and they have to be checked by hand.

    What the project's own code collects is never in a manifest unless it was written by hand, so it is
    always asked rather than guessed.
    """
    import os
    import plistlib

    from odevio.settings import console

    base = directory or os.getcwd()
    ios_directory = os.path.join(base, "ios")
    if not os.path.isdir(ios_directory):
        raise click.ClickException(
            f"No 'ios' directory in {base}. Run this from the root of a Flutter project.")

    manifests = _find_manifests(ios_directory)
    if not manifests:
        console.print("[warning]No privacy manifest found in this project.[/warning]")
        console.print(
            "If the dependencies were never installed, run [code]flutter pub get[/code] then "
            "[code]pod install[/code] in the ios directory, and scan again."
        )
        return

    own_manifest = None
    collected = {}
    accessed_apis = {}
    tracking_sources = []
    silent = []

    for path in manifests:
        try:
            with open(path, "rb") as manifest_file:
                content = plistlib.load(manifest_file)
        except Exception as error:  # A malformed manifest must not hide the rest of the report.
            console.print(f"[warning]Could not read {_source_name(ios_directory, path)}: {error}[/warning]")
            continue

        source = _source_name(ios_directory, path)
        if not _is_dependency(ios_directory, path):
            own_manifest = source

        if content.get("NSPrivacyTracking"):
            tracking_sources.append(source)

        declared = content.get("NSPrivacyCollectedDataTypes") or []
        if not declared:
            silent.append(source)
        for entry in declared:
            # App Privacy asks once per data type, not once per library, so several libraries declaring
            # the same type have to be merged into a single answer. They often disagree, and the answer
            # that keeps the app honest is the strictest one: if any library links the data to the user
            # or uses it for tracking, then the app does.
            data_type = entry.get("NSPrivacyCollectedDataType")
            record = collected.setdefault(
                data_type, {"purposes": set(), "sources": set(), "linked": False, "tracking": False,
                            "linked_by": set(), "tracking_by": set()})
            record["sources"].add(source)
            if entry.get("NSPrivacyCollectedDataTypeLinked"):
                record["linked"] = True
                record["linked_by"].add(source)
            if entry.get("NSPrivacyCollectedDataTypeTracking"):
                record["tracking"] = True
                record["tracking_by"].add(source)
            for purpose in entry.get("NSPrivacyCollectedDataTypePurposes") or []:
                record["purposes"].add(PURPOSE_LABELS.get(purpose, purpose))

        for entry in content.get("NSPrivacyAccessedAPITypes") or []:
            api_type = entry.get("NSPrivacyAccessedAPIType", "unknown")
            accessed_apis.setdefault(api_type, set()).update(
                entry.get("NSPrivacyAccessedAPITypeReasons") or [])

    console.print(f"Read [code]{len(manifests)}[/code] privacy manifest(s) under [code]ios/[/code].")
    console.print("")

    if collected:
        console.print("[title]What the privacy manifests declare is collected[/title]")
        console.print("Tick these in App Privacy, exactly as named:")
        console.print("")
        for data_type, record in sorted(
                collected.items(),
                key=lambda item: DATA_TYPE_LABELS.get(item[0], ("", str(item[0])))):
            category, label = DATA_TYPE_LABELS.get(data_type, ("Unknown category", data_type))
            console.print(f"  [code]{category} > {label}[/code]")
            console.print(f"      linked to the user: {'yes' if record['linked'] else 'no'}"
                          f"   used for tracking: {'yes' if record['tracking'] else 'no'}")
            if record["purposes"]:
                console.print(f"      purposes: {', '.join(sorted(record['purposes']))}")
            console.print(f"      declared by: {', '.join(sorted(record['sources']))}")
            # Naming who forced a yes matters: it is the only way to check the strict answer is right
            # rather than the consequence of one library over-declaring.
            disagreeing = []
            if record["linked"] and record["linked_by"] != record["sources"]:
                disagreeing.append(f"linked because of {', '.join(sorted(record['linked_by']))}")
            if record["tracking"] and record["tracking_by"] != record["sources"]:
                disagreeing.append(f"tracking because of {', '.join(sorted(record['tracking_by']))}")
            if disagreeing:
                console.print(f"      answered strictly: {'; '.join(disagreeing)}")
        console.print("")
    else:
        console.print("[title]Every manifest declares that nothing is collected[/title]")
        console.print("None of the libraries in this project says it collects anything.")
        console.print("")

    if tracking_sources:
        console.print("[warning]Some dependencies declare that they track users across apps:[/warning]")
        for source in sorted(set(tracking_sources)):
            console.print(f"  {source}")
        console.print("This makes the app subject to App Tracking Transparency.")
        console.print("")

    if accessed_apis:
        console.print("[title]Required-reason APIs used[/title]")
        console.print("Apple validates these on upload. They are declared already, nothing to do.")
        for api_type, reasons in sorted(accessed_apis.items()):
            console.print(f"  {api_type.replace('NSPrivacyAccessedAPICategory', '')}"
                          f"  ({', '.join(sorted(reasons))})")
        console.print("")

    console.print("[title]What no manifest can tell you[/title]")
    if own_manifest:
        console.print(f"Your own manifest is [code]{own_manifest}[/code]; it was included above.")
    else:
        console.print("Your app has no privacy manifest of its own, so nothing above covers the code you "
                      "wrote. Answer for it yourself:")
    console.print("")
    console.print("  - does your app ask people for a name, an email address or a phone number?")
    console.print("  - does it let people sign in, or create an account?")
    console.print("  - does it send anything to a server you control, and can that be traced back to a "
                  "person?")
    console.print("  - does it use analytics, crash reporting, or advertising?")
    console.print("  - is any of it used to follow people across other companies' apps or websites?")
    console.print("")
    if len(silent) == len(manifests) and not collected:
        console.print("[warning]Silence is not a guarantee.[/warning] A manifest declaring nothing means "
                      "the library says it collects nothing, not that it was verified.")
        console.print("")

    console.print("[title]Where this goes[/title]")
    console.print("App Store Connect > your app > App Privacy > Get Started. Apple does not allow this "
                  "to be filled in from the outside, so it is the one screen you have to visit yourself.")
    console.print("Two things worth knowing before you start:")
    console.print("  - only an [code]Admin[/code] on your Apple team may fill it in")
    console.print("  - the answers belong to the app, not to a version, so this is done once and never "
                  "again")


def _find_manifests(ios_directory):
    """ Collect every PrivacyInfo.xcprivacy under the ios directory.

    Manifests live wherever a library puts them — loose in a pod, inside a resource bundle, or within a
    framework — so the whole tree is walked rather than a handful of known locations.
    """
    import os

    found = []
    for root, _directories, files in os.walk(ios_directory):
        for name in files:
            if name == "PrivacyInfo.xcprivacy":
                found.append(os.path.join(root, name))
    return sorted(found)


def _is_dependency(ios_directory, path):
    import os

    relative = os.path.relpath(path, ios_directory)
    return relative.startswith("Pods" + os.sep) or ".framework" in relative or ".xcframework" in relative


def _source_name(ios_directory, path):
    """ Name a manifest by the library it belongs to rather than by its full path. """
    import os

    relative = os.path.relpath(path, ios_directory)
    parts = relative.split(os.sep)
    if parts[0] == "Pods" and len(parts) > 1:
        return parts[1]
    return relative
