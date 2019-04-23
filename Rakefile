require 'rake/clean'

CLEAN.include("*.class")

FIJI_DIR = File.expand_path("../../..")
FIJI_JAR_DIR = File.join(FIJI_DIR, "jars")
FIJI_PLUGIN_DIR = File.join(FIJI_DIR, "plugins")

PLUGIN_NAME = "LAMeasure"
PLUGIN_FILES = ["LAMeasure_.py", "CheckLeafNumbers_.py"]

desc "Copy files to plugin directory"
task :install => PLUGIN_FILES.map{|f| File.join(FIJI_PLUGIN_DIR, PLUGIN_NAME, f)}

PLUGIN_FILES.each do |f|
  to = File.join(FIJI_PLUGIN_DIR, PLUGIN_NAME, f)
  # desc "#{f} => #{to}"
  file to => [f] do |t|
    cp f, to
  end
end