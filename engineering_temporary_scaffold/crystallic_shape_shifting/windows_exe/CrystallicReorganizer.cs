using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;

internal sealed class PlannedMove
{
    public string source;
    public string destination;
    public string bucket;
    public string item_type;
    public string reason;
    public bool applied;
}

internal sealed class Options
{
    public string SourceRoot;
    public string DestinationRoot;
    public string StateFile;
    public bool Apply;
}

internal static class CrystallicReorganizerProgram
{
    private static readonly string[] Buckets = new[]
    {
        "core_geometry",
        "phase_transitions",
        "materials",
        "morphologies",
        "prototypes",
        "simulations",
        "state",
        "references",
    };

    private static readonly Dictionary<string, HashSet<string>> BucketKeywords =
        new Dictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase)
    {
        { "core_geometry", NewSet("anchor", "core", "crystal", "crystallic", "crystalline", "facet", "facets", "formseed", "geometry", "lattice", "shape", "symmetry") },
        { "phase_transitions", NewSet("collapse", "expand", "hinge", "metamorph", "phase", "shift", "shifting", "statechange", "transition", "transform", "transformation") },
        { "materials", NewSet("alloy", "ceramic", "coating", "composite", "fiber", "glass", "material", "materials", "metal", "natural", "polymer", "resin", "super") },
        { "morphologies", NewSet("body", "bodyplan", "edge", "facetmap", "family", "form", "morph", "morphologies", "morphology", "topology", "variant") },
        { "prototypes", NewSet("assembly", "build", "experiment", "fabricate", "fabrication", "mock", "prototype", "rig", "rigged") },
        { "simulations", NewSet("animate", "animation", "deform", "deformation", "motion", "render", "sim", "simulate", "simulation", "simulations", "stress") },
        { "state", NewSet("history", "index", "log", "manifest", "registry", "snapshot", "state", "timeline") },
    };

    private static readonly Dictionary<string, string> ExtensionBuckets =
        new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
    {
        { ".csv", "state" },
        { ".gif", "references" },
        { ".jpeg", "references" },
        { ".jpg", "references" },
        { ".json", "state" },
        { ".jsonl", "state" },
        { ".md", "references" },
        { ".pdf", "references" },
        { ".png", "references" },
        { ".py", "prototypes" },
        { ".rst", "references" },
        { ".svg", "references" },
        { ".toml", "state" },
        { ".txt", "references" },
        { ".webp", "references" },
        { ".yaml", "state" },
        { ".yml", "state" },
    };

    private static readonly HashSet<string> ReservedNames =
        new HashSet<string>(Buckets, StringComparer.OrdinalIgnoreCase)
        {
            "__init__.py",
            "incoming",
            "README.md",
            "reorganizer.py",
            "test_bed",
            "windows_exe",
        };

    private static int Main(string[] args)
    {
        try
        {
            var options = ParseOptions(args);
            var plan = BuildPlan(options);
            if (options.Apply)
            {
                ApplyPlan(plan);
            }

            WriteState(options, plan);
            PrintPlan(options, plan);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("ERROR: " + ex.Message);
            return 1;
        }
    }

    private static Options ParseOptions(string[] args)
    {
        string exeDir = AppDomain.CurrentDomain.BaseDirectory;
        string destinationRoot = Path.GetFullPath(Path.Combine(exeDir, ".."));
        string sourceRoot = Path.Combine(destinationRoot, "incoming");
        string stateFile = Path.Combine(destinationRoot, "state", "latest_reorganization_plan.json");
        bool apply = false;

        for (int index = 0; index < args.Length; index++)
        {
            string argument = args[index];
            if (string.Equals(argument, "--apply", StringComparison.OrdinalIgnoreCase))
            {
                apply = true;
                continue;
            }

            if (index + 1 >= args.Length)
            {
                throw new ArgumentException("Missing value for argument " + argument);
            }

            string value = args[index + 1];
            if (string.Equals(argument, "--source-root", StringComparison.OrdinalIgnoreCase))
            {
                sourceRoot = value;
            }
            else if (string.Equals(argument, "--destination-root", StringComparison.OrdinalIgnoreCase))
            {
                destinationRoot = value;
            }
            else if (string.Equals(argument, "--state-file", StringComparison.OrdinalIgnoreCase))
            {
                stateFile = value;
            }
            else
            {
                throw new ArgumentException("Unknown argument " + argument);
            }

            index += 1;
        }

        return new Options
        {
            SourceRoot = Path.GetFullPath(sourceRoot),
            DestinationRoot = Path.GetFullPath(destinationRoot),
            StateFile = Path.GetFullPath(stateFile),
            Apply = apply,
        };
    }

    private static List<PlannedMove> BuildPlan(Options options)
    {
        if (!Directory.Exists(options.SourceRoot))
        {
            throw new DirectoryNotFoundException("Source root does not exist: " + options.SourceRoot);
        }

        var entries = Directory.GetFileSystemEntries(options.SourceRoot)
            .OrderBy(path => Path.GetFileName(path), StringComparer.OrdinalIgnoreCase);
        var plan = new List<PlannedMove>();

        foreach (var entry in entries)
        {
            string name = Path.GetFileName(entry);
            if (name.StartsWith(".", StringComparison.Ordinal))
            {
                continue;
            }

            if (ReservedNames.Contains(name))
            {
                continue;
            }

            string reason;
            string bucket = Classify(entry, out reason);
            string destinationDir = Path.Combine(options.DestinationRoot, bucket);
            string destinationPath = GetUniqueDestination(Path.Combine(destinationDir, name));

            plan.Add(new PlannedMove
            {
                source = entry,
                destination = destinationPath,
                bucket = bucket,
                item_type = Directory.Exists(entry) ? "directory" : "file",
                reason = reason,
                applied = false,
            });
        }

        return plan;
    }

    private static string Classify(string path, out string reason)
    {
        HashSet<string> tokens = Tokenize(path);
        int bestScore = 0;
        string bestBucket = null;

        foreach (var pair in BucketKeywords)
        {
            int score = tokens.Count(token => pair.Value.Contains(token));
            if (score > bestScore || (score == bestScore && bestBucket != null && string.CompareOrdinal(pair.Key, bestBucket) < 0))
            {
                if (score > 0)
                {
                    bestScore = score;
                    bestBucket = pair.Key;
                }
            }
        }

        if (bestBucket != null)
        {
            reason = "keyword score " + bestScore + " from tokens " + string.Join(", ", tokens.OrderBy(token => token, StringComparer.Ordinal));
            return bestBucket;
        }

        string extension = Path.GetExtension(path);
        string extensionBucket;
        if (ExtensionBuckets.TryGetValue(extension, out extensionBucket))
        {
            reason = "extension fallback for " + extension.ToLowerInvariant();
            return extensionBucket;
        }

        reason = "default reference fallback";
        return "references";
    }

    private static HashSet<string> Tokenize(string path)
    {
        string name = Path.GetFileName(path);
        string stem = Path.GetFileNameWithoutExtension(path);
        string raw = File.Exists(path) ? stem + " " + name : name;
        var tokens = new HashSet<string>(
            Regex.Split(raw.ToLowerInvariant(), "[^a-z0-9]+").Where(token => !string.IsNullOrEmpty(token)),
            StringComparer.OrdinalIgnoreCase
        );

        foreach (var token in tokens.ToList())
        {
            if (token.Contains("transform"))
            {
                tokens.Add("transform");
                tokens.Add("transformation");
            }
            if (token.Contains("transition"))
            {
                tokens.Add("transition");
            }
            if (token.Contains("morph"))
            {
                tokens.Add("morph");
                tokens.Add("morphology");
            }
            if (token.Contains("material"))
            {
                tokens.Add("material");
                tokens.Add("materials");
            }
            if (token.Contains("sim"))
            {
                tokens.Add("sim");
            }
            if (token.Contains("crystal"))
            {
                tokens.Add("crystal");
            }
        }

        return tokens;
    }

    private static string GetUniqueDestination(string destination)
    {
        if (!File.Exists(destination) && !Directory.Exists(destination))
        {
            return destination;
        }

        string directory = Path.GetDirectoryName(destination);
        string baseName = Path.GetFileNameWithoutExtension(destination);
        string extension = Path.GetExtension(destination);
        int counter = 1;

        while (true)
        {
            string candidate = Path.Combine(directory, baseName + "_" + counter + extension);
            if (!File.Exists(candidate) && !Directory.Exists(candidate))
            {
                return candidate;
            }

            counter += 1;
        }
    }

    private static void ApplyPlan(IEnumerable<PlannedMove> plan)
    {
        foreach (var move in plan)
        {
            string parent = Path.GetDirectoryName(move.destination);
            if (!Directory.Exists(parent))
            {
                Directory.CreateDirectory(parent);
            }

            if (string.Equals(move.item_type, "directory", StringComparison.OrdinalIgnoreCase))
            {
                Directory.Move(move.source, move.destination);
            }
            else
            {
                File.Move(move.source, move.destination);
            }

            move.applied = true;
        }
    }

    private static void WriteState(Options options, IEnumerable<PlannedMove> plan)
    {
        string parent = Path.GetDirectoryName(options.StateFile);
        if (!Directory.Exists(parent))
        {
            Directory.CreateDirectory(parent);
        }

        var serializer = new JavaScriptSerializer();
        var payload = new Dictionary<string, object>
        {
            { "generated_at", DateTime.UtcNow.ToString("o") },
            { "mode", options.Apply ? "apply" : "dry-run" },
            { "source_root", options.SourceRoot },
            { "destination_root", options.DestinationRoot },
            {
                "moves",
                plan.Select(move => new Dictionary<string, object>
                {
                    { "source", move.source },
                    { "destination", move.destination },
                    { "bucket", move.bucket },
                    { "item_type", move.item_type },
                    { "reason", move.reason },
                    { "applied", move.applied },
                }).ToList()
            },
        };

        File.WriteAllText(options.StateFile, serializer.Serialize(payload));
    }

    private static void PrintPlan(Options options, IList<PlannedMove> plan)
    {
        Console.WriteLine("[" + (options.Apply ? "APPLY" : "DRY RUN") + "] Crystallic reorganizer");
        Console.WriteLine("Source: " + options.SourceRoot);
        Console.WriteLine("Destination: " + options.DestinationRoot);
        Console.WriteLine("Plan file: " + options.StateFile);

        if (plan.Count == 0)
        {
            Console.WriteLine("No movable files or folders were found.");
            return;
        }

        Console.WriteLine("Planned moves: " + plan.Count);
        foreach (var move in plan)
        {
            Console.WriteLine("- " + move.item_type + ": " + move.source + " -> " + move.destination + " [" + move.bucket + "]");
            Console.WriteLine("  reason: " + move.reason);
        }
    }

    private static HashSet<string> NewSet(params string[] values)
    {
        return new HashSet<string>(values, StringComparer.OrdinalIgnoreCase);
    }
}
