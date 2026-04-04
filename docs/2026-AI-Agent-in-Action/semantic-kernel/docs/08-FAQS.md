# 자주 묻는 질문

### 나이틀리 빌드에 어떻게 접근하나요?

Semantic Kernel의 나이틀리 빌드는 [여기](https://github.com/orgs/microsoft/packages?repo_name=semantic-kernel)에서 사용할 수 있습니다.

나이틀리 빌드를 다운로드하려면 다음 단계를 따르세요:

1. 이 단계를 완료하려면 GitHub 계정이 필요합니다.
1. 다음 [안내](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)를 참고하여 `read:packages` 스코프를 가진 GitHub Personal Access Token을 생성합니다.
1. 계정이 Microsoft 조직에 속해 있다면 `Microsoft` 조직을 단일 로그인(SSO) 조직으로 인가해야 합니다.
    1. 방금 생성한 Personal Access Token 옆의 "Configure SSO"를 클릭한 다음 `Microsoft`를 인가합니다.
1. 다음 명령어를 사용하여 Microsoft GitHub Packages 소스를 NuGet 구성에 추가합니다:

    ```powershell
    dotnet nuget add source --username GITHUBUSERNAME --password GITHUBPERSONALACCESSTOKEN --store-password-in-clear-text --name GitHubMicrosoft "https://nuget.pkg.github.com/microsoft/index.json"
    ```

1. 또는 `NuGet.Config` 파일을 수동으로 생성할 수 있습니다.

    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <configuration>
      <packageSources>
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />
        <add key="github" value="https://nuget.pkg.github.com/microsoft/index.json" />
      </packageSources>
    
      <packageSourceMapping>
        <packageSource key="nuget.org">
          <package pattern="*" />
        </packageSource>
        <packageSource key="github">
          <package pattern="*nightly"/>
        </packageSource>
      </packageSourceMapping>
    
      <packageSourceCredentials>
        <github>
            <add key="Username" value="<Your GitHub Id>" />
            <add key="ClearTextPassword" value="<Your Personal Access Token>" />
          </github>
      </packageSourceCredentials>
    </configuration>
    ```

    * 이 파일을 프로젝트 폴더에 배치하는 경우 Git(또는 사용 중인 소스 제어 도구)이 이 파일을 무시하도록 설정하세요.
    * 이 파일을 저장할 위치에 대한 자세한 정보는 [여기](https://learn.microsoft.com/en-us/nuget/reference/nuget-config-file)를 참고하세요.
    * 다음 명령어를 사용하여 Microsoft GitHub Packages 소스를 NuGet에 더 쉽게 추가할 수도 있습니다:
1. 이제 나이틀리 빌드의 패키지를 프로젝트에 추가할 수 있습니다.
    * 예: 이 명령어를 사용하세요 `dotnet add package Microsoft.SemanticKernel.Core --version 0.26.231003.1-nightly`
1. 최신 패키지 릴리스는 프로젝트에서 다음과 같이 참조할 수 있습니다:
    * `<PackageReference Include="Microsoft.SemanticKernel" Version="*-*" />`

자세한 정보는 다음을 참고하세요: <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-nuget-registry>
