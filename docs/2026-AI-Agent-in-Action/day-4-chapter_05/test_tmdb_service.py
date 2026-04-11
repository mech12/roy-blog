import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments

# 사용 시
args = KernelArguments(genre_name="action")
from plugins.Movies.tmdb import TMDbService


async def main():
    # Initialize the kernel
    kernel = sk.Kernel()

    tmdb_service = kernel.add_plugin(TMDbService(), "TMDBService")

    # Test the function with the inputs.
    # uncomment the line to test the function
    print(
        await tmdb_service["get_movie_genre_id"](
            kernel, KernelArguments(genre_name="action")
        )
    )
    print(
        await tmdb_service["get_tv_show_genre_id"](
            kernel, KernelArguments(genre_name="action")
        )
    )
    print(
        await tmdb_service["get_top_movies_by_genre"](
            kernel, KernelArguments(genre_name="action")
        )
    )
    print(
        await tmdb_service["get_top_tv_shows_by_genre"](
            kernel, KernelArguments(genre_name="action")
        )
    )
    print(await tmdb_service["get_movie_genres"](kernel, KernelArguments()))
    print(await tmdb_service["get_tv_show_genres"](kernel, KernelArguments()))


# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
